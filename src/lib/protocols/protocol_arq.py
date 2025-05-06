from abc import abstractmethod
import zlib
DATA_CHUNK_SIZE = 256
DELIM = "-----------------------------------"
IND = "     "


class ProtocolARQ:
    def __init__(self, socket, remote_address, is_verbose):
        self.socket = socket
        self.address = remote_address
        self.is_verbose = is_verbose

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

    def _print_if_verbose(self, msg):
        if self.is_verbose:
            print(msg)


    def _bool_to_byte(self,flag: bool) -> bytes:
        """
        Convierte un booleano a un byte:
        True  → b'\x01'
        False → b'\x00'
        """
        return (1).to_bytes(1, byteorder='big') if flag else (0).to_bytes(1, byteorder='big')

    def _byte_to_bool(self,b: bytes) -> bool:
        """
        Convierte un byte de longitud 1 de vuelta a booleano:
        b'\x01' → True
        b'\x00' → False
        """
        return bool(b[0])
    
    def _get_checksum_data(self, data: bytes) -> bytes:
        """
        Encripta los datos usando XOR con una clave fija. Devuelve 4 bytes.
        """
        crc = zlib.crc32(data) & 0xFFFFFFFF
        return crc.to_bytes(4, byteorder='big')