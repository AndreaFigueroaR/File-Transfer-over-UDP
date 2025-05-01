from abc import ABC, abstractmethod

TIMEOUT = 1

# Este CHUNK_SIZE no es necesariamente el mismo que el de la capa de aplicación.
CHUNK_SIZE = 256


class ProtocolARQ:
    def __init__(self, socket, local_sn, remote_sn, remote_address, is_verbose):
        self.socket = socket
        self.local_sn = local_sn
        self.remote_sn = remote_sn
        self.address = remote_address
        self.is_verbose = is_verbose

    @abstractmethod
    def send(self, data: bytes):
        pass

    @abstractmethod
    def receive(self, max_size) -> bytearray:
        pass

    @abstractmethod
    def stop(self):
        pass

    def _print_if_verbose(self, msg):
        if self.is_verbose:
            print(msg)

    def stop(self):
        self.socket.close()