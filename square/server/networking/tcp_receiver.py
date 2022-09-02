from threading import Thread

from square import BUFFER_SIZE


class TCPReceiver(Thread):
    """Creates a new thread to receive TCP data from a specific client"""

    def __init__(self, socket, message_queue, disconnect_queue):
        super().__init__()
        self.running = False
        self.socket = socket
        self.message_queue = message_queue
        self.disconnect_queue = disconnect_queue

    def run(self):
        self.running = True
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE).decode("utf-8")
                self.message_queue.put(data)
            finally:
                break

        self.disconnect_queue.put(self.socket)
