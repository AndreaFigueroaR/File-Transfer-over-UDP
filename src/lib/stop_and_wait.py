from lib.protocol_arq import ProtocolARQ, TIMEOUT, CHUNK_SIZE
import socket

NUM_ATTEMPS = 10
DELIM = "-----------------------------------"
IND = "     "

class StopAndWait(ProtocolARQ):
    def send(self, data: bytes):
        if len(data) == 0:
            self._send_ack(self.remote_sn)
            self._update_expected_seq_num()
            return
        
        self._print_if_verbose(f"Data size to send: {len(data)}")
        for i in range(0, len(data), CHUNK_SIZE):
            data_chunk = data[i:i + CHUNK_SIZE]
            self._send_segment(data_chunk)

    def _send_ack(self, ack):
        ack_b = ack.to_bytes(1, byteorder='big')
        self.socket.sendto(ack_b, self.address)

    # TODO : hacer parte del header de cada segmento el largo del payload
    # (aparte del numero de secuencia)
    def _send_segment(self, data_chunk: bytes):
        seq_num_byte = self.remote_sn.to_bytes(1, byteorder='big')
        segment = seq_num_byte + data_chunk
        
        for _ in range(NUM_ATTEMPS):
            try:
                self._print_if_verbose(f"{IND}{DELIM}")
                self._print_if_verbose(f"{IND}Segment size to send: {len(segment)}")
                
                self.socket.sendto(segment, self.address)
                
                ack = self._recv_ack()
                if ack != self.remote_sn:
                    self._print_if_verbose(f"{IND}Received unexpected ACK.")
                else:
                    self._print_if_verbose(f"{IND}Received expected ACK.")
                    self._update_expected_seq_num()
                    return
            except socket.timeout:
                self._print_if_verbose(f"{IND}[ERROR]: Timeout")
        raise ConnectionError(
            "[Error]: failed to send segment after multiple attempts")

    def receive(self, max_data_size) -> bytearray:
        data = bytearray()
        bytes_received = 0

        while bytes_received < max_data_size:
            try:
                seq_num, payload = self._recv_segment()

                if seq_num != self.remote_sn:
                    self._print_if_verbose(f"Received unexpected sequence number.")
                    self._send_ack(1 - self.remote_sn)
                else:
                    self._print_if_verbose(f"Received expected sequence number.")
                    data.extend(payload)
                    bytes_received += len(payload)
                    self._send_ack(seq_num)
                    self._update_expected_seq_num()
                    if len(payload) < CHUNK_SIZE:
                        return data
            except socket.timeout:
                print("[Error]: Timeout")
                self._send_ack(1 - self.remote_sn)
        return data

    def _recv_ack(self):
        segment, _ = self.socket.recvfrom(1 + CHUNK_SIZE)
        ack = int.from_bytes(segment[0:1], byteorder='big')
        self._print_if_verbose(f"{IND}ACK expected: {self.remote_sn}")
        self._print_if_verbose(f"{IND}ACK received: {ack}")
        return ack

    def _recv_segment(self):
        segment, _ = self.socket.recvfrom(1 + CHUNK_SIZE)
        seq_num = int.from_bytes(segment[0:1], byteorder='big')
        payload = segment[1:]
        
        self._print_if_verbose(DELIM)
        self._print_if_verbose(f"Segment size to recieve: {len(segment)}")
        self._print_if_verbose(f"Sequence number expected: {self.remote_sn}")
        self._print_if_verbose(f"Sequence number received: {seq_num}")
        return seq_num, payload

    def _update_expected_seq_num(self):
        self.remote_sn = 1 - self.remote_sn
