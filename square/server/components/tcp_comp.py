import socket

from square.server.networking import TCPReceiver


class TCPComponent:
    def __init__(self, socket, message_queue, disconnect_queue):
        self.socket = socket
        self.tcp_receiver = TCPReceiver(self.socket, message_queue, disconnect_queue)
        self.tcp_receiver.start()

    def disconnect(self):
        self.socket.shutdown(socket.SHUT_RD)
        self.socket.close()
        self.tcp_receiver.join()
