import queue
import socket
import sys
from typing import Optional

from square import UDP_SEND_INTERVAL
from square.common.application import Application
from square.common.components import PhysicsComponent, SpriteComponent
from square.server import clock
from square.server.components import TCPComponent
from square.server.networking import TCPConnectionListener, UDPReceiver

_server: Optional["ServerApplication"] = None


def get_server() -> "ServerApplication":
    if _server is None:
        raise RuntimeError(
            "No server is active. Use set_window() to set an active window"
        )

    return _server


def set_server(server: "ServerApplication") -> None:
    global _server
    _server = server


class ServerApplication(Application):
    def __init__(
        self,
        address: str,
        port: int,
    ):
        super().__init__()

        self.address = address
        self.port = port

        # Networking Stuff
        self.tcp_socket = None
        self.udp_socket = None
        self.client_connection_queue = None
        self.client_disconnect_queue = None
        self.client_message_queue = None
        self.client_update_queue = None
        self.tcp_connector = None
        self.udp_receiver = None
        self.entity_tcp_receivers = None

        set_server(self)

    def start(self):
        # Setup TCP Handling
        self.client_connection_queue = queue.Queue()
        self.client_disconnect_queue = queue.Queue()
        self.client_message_queue = queue.Queue()
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind((self.address, self.port))
        self.tcp_socket.listen()
        if self.port == 0:
            self.port = self.tcp_socket.getsockname()[1]
        self.tcp_connector = TCPConnectionListener(
            self.tcp_socket, self.client_connection_queue
        )
        self.entity_tcp_receivers = {}
        self.tcp_connector.daemon = True
        self.tcp_connector.start()

        # Setup UDP Handling
        self.client_update_queue = queue.Queue()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.address, self.port))
        self.udp_receiver = UDPReceiver(self.udp_socket, self.client_update_queue)
        self.udp_receiver.daemon = True
        self.udp_receiver.start()

        self.clock = clock.get_default()

        self.run()

    def tick_step(self):
        self.can_step = True

    def run(self):
        self.running = True
        self.clock.schedule_interval(self.send_udp, UDP_SEND_INTERVAL)
        self.clock.schedule_interval(self.on_update, 1 / 60)
        try:
            while self.running:
                self.clock.tick()
        except KeyboardInterrupt:
            sys.exit()

    def send_udp(self, delta_time):
        """Send all player data to each connected Client"""

        # There is a race condition where a client can disconnect but
        # still be in the players listing of the server for enough time
        # for it to be sent with this. So we need to process any
        # disconnects that may have happened between the last on_update
        # and now
        self.process_client_disconnects()

        data = ""
        for client_id, client in self.players.items():
            # Add address for this client to the data
            data += f"{client_id};"
            # Add the velocity for the body to the data
            phys = self.world.component_for_entity(client, PhysicsComponent)
            data += f"{phys.velocity[0]};{phys.velocity[1]};"
            # Add the actual sprite position
            sprite = self.world.component_for_entity(client, SpriteComponent).sprite
            data += f"{sprite.center_x};{sprite.center_y};"
            # Add an extra ;; delimiter to separate players
            data += ";"
        # Encode data minus the last ;; delimiter
        data = data[:-2].encode()
        # Send data to all connected clients
        for id in self.players:
            id_split = id.split(":")
            self.udp_socket.sendto(data, (id_split[0], int(id_split[1])))

    def new_client(self, socket, id):
        entity = self.add_player(id, 100, 100)
        self.world.add_component(
            entity,
            TCPComponent(
                socket, self.client_message_queue, self.client_disconnect_queue
            ),
        )

        for entity in self.players.values():
            tcp_comp = self.world.component_for_entity(entity, TCPComponent)
            tcp_comp.socket.sendall(f"client_connect;;{id};;100;;100".encode())

    def remove_client(self, id):
        entity = self.players[id]
        tcp_comp = self.world.component_for_entity(entity, TCPComponent)
        tcp_comp.disconnect()
        self.remove_player(id)

        # Inform all other clients of the disconnect
        for entity in self.players.values():
            tcp_comp = self.world.component_for_entity(entity, TCPComponent)
            tcp_comp.socket.sendall(f"client_disconnect;;{id}".encode())

    def on_update(self, delta_time: float):
        """Game Logic"""
        super().on_update(delta_time)

        self.process_client_connections()
        self.process_client_disconnects()
        self.process_client_messages()
        self.process_client_updates()

    def process_client_connections(self):
        connections = []
        while not self.client_connection_queue.empty():
            connections.append(self.client_connection_queue.get())
        if not connections:
            return

        for connection in connections:
            self.new_client(connection[0], connection[1])

    def process_client_disconnects(self):
        disconnects = []
        while not self.client_disconnect_queue.empty():
            disconnects.append(self.client_disconnect_queue.get())
        if not disconnects:
            return

        for disconnect in disconnects:
            id = disconnect.getpeername()
            if id in self.players:
                self.remove_client(id)

    def process_client_messages(self):
        messages = []
        while not self.client_message_queue.empty():
            messages.append(self.client_message_queue.get())
        if not messages:
            return

        for message in messages:
            # We don't actually have any TCP messages from clients right now
            # outside of connections, which are handled separately.
            # This would be used for things like chat messages or something
            pass

    def process_client_updates(self):
        updates = []
        while not self.client_update_queue.empty():
            updates.append(self.client_update_queue.get())
        if not updates:
            return

        for update in updates:
            if update[0] in self.players:
                entity = self.players[update[0]]
                phys = self.world.component_for_entity(entity, PhysicsComponent)
                sprite = self.world.component_for_entity(entity, SpriteComponent)
                data = [float(val) for val in update[1][0].split(";")]
                phys.velocity[0] = data[0]
                phys.velocity[1] = data[1]
                sprite.sprite.center_x = data[2]
                sprite.sprite.center_y = data[3]
