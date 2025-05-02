from lib.protocols.protocol_arq import *
import socket

NUM_ATTEMPS = 10


class StopAndWait(ProtocolARQ):
    def send(self, data: bytes):
        current_sn = 0
        if len(data) == 0:
            self._send_ack(current_sn)
            return
        
        self._print_if_verbose(f"Data size to send: {len(data)}")
        
        data_chunks = self._split_data(data)
        for chunk in data_chunks:
            self._send_data_chunk(current_sn, chunk)
            current_sn = 1 - current_sn

    def _send_data_chunk(self, segment_sn, data_chunk: bytes):
        for _ in range(NUM_ATTEMPS):
            try:
                self._send_segment(segment_sn, data_chunk)
                
                ack = self._recv_ack()
                self._print_if_verbose(f"{IND}ACK expected: {segment_sn}")
                self._print_if_verbose(f"{IND}ACK received: {ack}")
                if ack != segment_sn:
                    self._print_if_verbose(f"{IND}Received unexpected ACK.")
                else:
                    self._print_if_verbose(f"{IND}Received expected ACK.")
                    return
            except socket.timeout:
                self._print_if_verbose(f"{IND}[ERROR]: Timeout")
        raise ConnectionError(
            "[ERROR]: failed to send segment after multiple attempts")

    def receive(self, max_data_size) -> bytearray:
        expected_sn = 0
        data = bytearray()
        bytes_received = 0

        while bytes_received < max_data_size:
            try:
                seq_num, payload = self._recv_segment()
                self._print_if_verbose(f"Sequence number expected: {expected_sn}")
                self._print_if_verbose(f"Sequence number received: {seq_num}")

                if seq_num != expected_sn:
                    self._print_if_verbose(f"Received unexpected sequence number.")
                    self._send_ack(1 - expected_sn)
                else:
                    self._print_if_verbose(f"Received expected sequence number.")
                    data.extend(payload)
                    bytes_received += len(payload)
                    self._send_ack(seq_num)
                    if len(payload) < DATA_CHUNK_SIZE:
                        return data
                    expected_sn = 1 - expected_sn
            except socket.timeout:
                print("[ERROR]: Timeout")
                self._send_ack(1 - expected_sn)
        return data
