import zlib


class Serializer:
    @staticmethod
    def bool_to_byte(flag: bool) -> bytes:
        """
        Convert boolean to byte:
        True  → b'\x01'
        False → b'\x00'
        """
        return (1).to_bytes(1, byteorder='big') if flag else (
            0).to_bytes(1, byteorder='big')

    @staticmethod
    def byte_to_bool(b: bytes) -> bool:
        """
        Convert byte to boolean:
        b'\x01' → True
        b'\x00' → False
        """
        return bool(b[0])

    @staticmethod
    def get_checksum_data(data: bytes) -> bytes:
        """
        Encrypts the data using XOR with a fixed key. Returns 4 bytes.
        """
        crc = zlib.crc32(data) & 0xFFFFFFFF
        return crc.to_bytes(4, byteorder='big')

    @staticmethod
    def is_about_handhshake(data: bytes) -> bool:
        return Serializer.byte_to_bool(data[0:1])
