from threading import Thread

from square import BUFFER_SIZE


class TCPReceiver(Thread):
    def __init__(self, socket, queue):
        super().__init__()
        self.running = False
        self.socket = socket
        self.queue = queue

    def run(self):
        self.running = True
        while self.running:
            data = self.socket.recv(BUFFER_SIZE).decode("utf-8")
            self.queue.put(data)
