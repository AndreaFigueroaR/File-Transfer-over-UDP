from abc import abstractmethod
DATA_CHUNK_SIZE = 1024
DELIM = "-----------------------------------"
IND = "     "


class ProtocolARQ:
    def __init__(self, socket, remote_address):
        self.socket = socket
        self.address = remote_address

    @abstractmethod
    def send(self, data: bytes):
        pass

    @abstractmethod
    def receive(self, max_data_size) -> bytearray:
        pass

    def _split_data(self, data: bytes):
        data_chunks = []
        for i in range(0, len(data), DATA_CHUNK_SIZE):
            data_chunks.append(data[i:i + DATA_CHUNK_SIZE])
        return data_chunks
