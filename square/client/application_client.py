import queue
import socket
import time
from typing import Optional

import arcade

import square.client
from square import UDP_SEND_INTERVAL
from square.client.components import DRComponent, InputComponent
from square.client.networking import TCPReceiver, UDPReceiver
from square.client.processors import DRProcessor, InputProcessor
from square.common.application import Application
from square.common.components import PhysicsComponent, SpriteComponent

_application: Optional["ClientApplication"] = None


def set_application(application: "ClientApplication") -> None:
    global _application
    _application = application


def get_application() -> "ClientApplication":
    if _application is None:
        raise RuntimeError("No application is active.")

    return _application


class ClientApplication(Application):
    def __init__(self, address):
        super().__init__()
        self.server_address = address

        # Networking Things
        self.my_address = None
        self.my_entity = None
        self.tcp_socket = None
        self.udp_socket = None
        self.server_message_queue = None
        self.server_update_queue = None
        self.tcp_receiver = None
        self.udp_receiver = None

        self.time = None

        self.client_input = {
            "left": 0,
            "right": 0,
            "up": 0,
            "down": 0,
        }

        self.world.add_processor(InputProcessor())
        self.world.add_processor(DRProcessor())

        square.client.get_window().register_application(self)

    def start(self):

        # Setup TCP Handling
        self.server_message_queue = queue.Queue()
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.connect(self.server_address)
        address = self.tcp_socket.getsockname()
        self.my_address = f"{address[0]}:{address[1]}"
        self.tcp_receiver = TCPReceiver(self.tcp_socket, self.server_message_queue)
        self.tcp_receiver.daemon = True
        self.tcp_receiver.start()

        # Setup UDP Handling
        self.server_update_queue = queue.Queue()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(address)
        self.udp_receiver = UDPReceiver(self.udp_socket, self.server_update_queue)
        self.udp_receiver.daemon = True
        self.udp_receiver.start()

        # Schedule client's send_udp function
        arcade.schedule(self.send_udp, UDP_SEND_INTERVAL)

    def stop(self):
        arcade.unschedule(self.send_udp)

        # Shutdown TCP
        self.tcp_receiver.running = False
        self.tcp_socket.shutdown(socket.SHUT_RD)
        self.tcp_socket.close()
        self.tcp_receiver.join()

        # Shutdown UDP
        self.udp_receiver.running = False
        # FIXME This try-catch is a god awful work-around for a problem I don't
        # understand to prevent this OSError from cluttering logs. It doesn't
        # really break anything, so whatever, maybe this is fine. All I know is
        # the socket will not close without this shutdown before-hand.
        try:
            self.udp_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.udp_socket.close()
        self.udp_receiver.join()

    def new_player(self, id, x, y):
        self.add_player(id, x, y)
        self.world.add_component(self.players[id], DRComponent())
        self.world.add_component(self.players[id], InputComponent())
        if id == self.my_address:
            self.my_entity = self.players[id]

    def input(self):
        return self.world.component_for_entity(self.my_entity, InputComponent)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.input().up = 1
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.input().left = 1
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.input().right = 1
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.input().down = 1

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.input().up = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.input().left = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.input().right = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.input().down = 0

    def on_update(self, delta_time):
        super().on_update(delta_time)

        self.process_server_messages()
        self.process_server_updates()

        self.world.process(delta_time=delta_time, excludes=[self.my_entity])

    def process_server_messages(self):
        messages = []
        while not self.server_message_queue.empty():
            messages.append(self.server_message_queue.get())
        if not messages:
            return

        for message in messages:
            self.process_server_message(message)

    def process_server_message(self, message):
        message = message.split(";;")
        command = message[0]
        if command == "client_connect":
            # A new player joined the game
            self.new_player(message[1], float(message[2]), float(message[3]))
        elif command == "client_disconnect":
            # A player has left the game
            self.remove_player(message[1])

    def process_server_updates(self):
        updates = []
        while not self.server_update_queue.empty():
            updates.append(self.server_update_queue.get())
        if not updates:
            return

        for update in updates:
            self.process_server_update(update)

    def process_server_update(self, update):
        update = update.split(";;")
        for player_data in update:
            player_data = player_data.split(";")
            player_id = player_data[0]
            if player_id not in self.players:
                self.new_player(
                    player_id,
                    float(player_data[3]),
                    float(player_data[4]),
                )
                continue
            if player_id != self.my_address:
                self.update_player(self.players[player_id], player_data[1:])

    def update_player(self, player, data):
        dr_comp = self.world.component_for_entity(player, DRComponent)
        dr_comp.previous_position = dr_comp.position
        dr_comp.previous_velocity = dr_comp.velocity
        dr_comp.previous_time = dr_comp.time
        dr_comp.position = (float(data[2]), float(data[3]))
        dr_comp.velocity = (float(data[0]), float(data[1]))
        dr_comp.time = time.time()
        accel_x = (dr_comp.velocity[0] - dr_comp.previous_velocity[0]) / (
            dr_comp.time - dr_comp.previous_time
        )
        accel_y = (dr_comp.velocity[1] - dr_comp.previous_velocity[1]) / (
            dr_comp.time - dr_comp.previous_time
        )
        dr_comp.acceleration = (accel_x, accel_y)

    def send_udp(self, delta_time):
        if not self.my_entity:
            return

        data = ""
        phys = self.world.component_for_entity(self.my_entity, PhysicsComponent)
        sprite = self.world.component_for_entity(self.my_entity, SpriteComponent)
        data += f"{phys.velocity[0]};{phys.velocity[1]};"
        data += f"{sprite.sprite.center_x};{sprite.sprite.center_y}"
        self.udp_socket.sendto(data.encode(), self.server_address)
