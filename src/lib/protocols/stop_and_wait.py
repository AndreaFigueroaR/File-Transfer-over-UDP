from lib.protocols.protocol_arq import *
import socket

NUM_ATTEMPS = 10
FIRST_SN = 0
FIN = 2

class StopAndWait(ProtocolARQ):
    def send(self, data):
        total_len = len(data)
        self._print_if_verbose(f"Data size to send: {total_len}")
        data_chunks = self._split_data(data)
        sn = FIRST_SN
        for chunk in data_chunks:
            self._send_data_chunk(sn, chunk)
            sn = 1 - sn
        self._send_data_chunk(sn, bytes())

    def _send_data_chunk(self, sn, chunk):
        for _ in range(NUM_ATTEMPS):
            try:
                self._send_segment(sn, chunk)

                if not chunk:
                    self._eof_sender_handshake()
                    return

                ack = self._recv_ack()
                if ack == sn:
                    self._print_if_verbose(f"{IND}Received expected ACK: {ack}")
                    return
                else: 
                    self._print_if_verbose(f"{IND}Received unexpected ACK: {ack}")
            except socket.timeout:
                self._print_if_verbose("TIMEOUT: Try again")
        raise ConnectionError("Failed to send segment after multiple attempts")

    def receive(self):
        bytes_received = 0
        data = bytearray()
        expected_sn = FIRST_SN
        while True:
            try:
                sn, payload = self._recv_segment()
                if not payload:
                    self._eof_receiver_handshake()
                    return data
                if sn == expected_sn:
                    data.extend(payload)
                    bytes_received += len(payload)
                    expected_sn = 1 - expected_sn
                else:
                    self._print_if_verbose(f"Duplicate SN {sn}, re-acked but not re-appended")
                self._send_ack(sn)
                self._print_if_verbose(f"Payload bytes received: {bytes_received}")
            except socket.timeout:
                self._print_if_verbose("TIMEOUT: Try again")
    
    def _eof_receiver_handshake(self):
        while True:
            try:
                self._send_ack(FIN)
                ack = self._recv_ack()
                if ack == FIN:
                    return
            except socket.timeout:
                self._print_if_verbose("TIMEOUT on End-Of-File handshake: Try again")
    
    def _eof_sender_handshake(self):
        while True:
            try:
                ack = self._recv_ack()
                if ack == FIN:
                    self._send_ack(FIN)
                    return
            except socket.timeout:
                self._print_if_verbose("TIMEOUT on End-Of-File handshake: Try again")
