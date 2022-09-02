from threading import Thread

from square import BUFFER_SIZE


class UDPReceiver(Thread):
    def __init__(self, socket, queue):
        super().__init__()
        self.running = False
        self.socket = socket
        self.queue = queue

    def run(self):
        self.running = True
        while self.running:
            data, address = self.socket.recvfrom(BUFFER_SIZE)
            data = data.decode("utf-8").split(";;", 1)
            self.queue.put((f"{address[0]}:{address[1]}", data))
