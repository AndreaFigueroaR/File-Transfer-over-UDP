from abc import abstractmethod

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

    def _send_ack(self, ack):
        ack_b = ack.to_bytes(1, byteorder='big')
        self.socket.sendto(ack_b, self.address)

    def _send_segment(self, segment_sn, data_chunk: bytes):
        self._print_if_verbose(f"{IND}{DELIM}")
        self._print_if_verbose(f"{IND}Segment size to send: {1 + len(data_chunk)}")
        
        seq_num_byte = segment_sn.to_bytes(1, byteorder='big')
        segment = seq_num_byte + data_chunk
        self.socket.sendto(segment, self.address)

    @abstractmethod
    def receive(self, max_data_size) -> bytearray:
        pass

    def _recv_ack(self):
        segment, _ = self.socket.recvfrom(1)
        ack = int.from_bytes(segment[0:1], byteorder='big')
        return ack

    def _recv_segment(self):
        segment, _ = self.socket.recvfrom(1 + DATA_CHUNK_SIZE)
        seq_num = int.from_bytes(segment[0:1], byteorder='big')
        payload = segment[1:]
        
        self._print_if_verbose(DELIM)
        self._print_if_verbose(f"Segment size recieved: {len(segment)}")
        return seq_num, payload

    def _split_data(self, data: bytes):
        data_chunks = []
        for i in range(0, len(data), DATA_CHUNK_SIZE):
            data_chunks.append(data[i:i + DATA_CHUNK_SIZE])
        return data_chunks

    def _print_if_verbose(self, msg):
        if self.is_verbose:
            print(msg)

    def stop(self):
        self.socket.close()
