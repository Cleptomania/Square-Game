from threading import Thread


class TCPConnectionListener(Thread):
    """Waits for TCP connections and creates new clients."""

    def __init__(self, socket, queue):
        super().__init__()
        self.running = False
        self.socket = socket
        self.queue = queue

    def run(self):
        self.running = True
        while self.running:
            client_socket, address = self.socket.accept()
            self.queue.put((client_socket, f"{address[0]}:{address[1]}"))
