from lib.protocols.protocol_arq import *
import socket

NUM_ATTEMPS = 10
FIRST_SN = 0
FIN = 2

class StopAndWait(ProtocolARQ):
    def send(self, data):
        self._print_if_verbose(f"Data size to send: {len(data)}")
        data_chunks = self._split_data(data)
        sn = FIRST_SN
        for chunk in data_chunks:
            self._send_data_chunk(sn, chunk)
            sn = 1 - sn
        self._send_data_chunk(FIN, bytes())

    def _send_data_chunk(self, sn, chunk):
        for _ in range(NUM_ATTEMPS):
            try:
                self._send_segment(sn, chunk)

                ack = self._recv_ack()
                if ack == sn:
                    self._print_if_verbose(f"{IND}Received expected ACK: {ack}")
                    return
                if ack == FIN:
                    self._print_if_verbose("Reach End-Of-Data.")
                    return
                self._print_if_verbose(f"{IND}Received unexpected ACK: {ack}")
            except socket.timeout:
                if sn == FIN:
                    self._print_if_verbose("Reach End-Of-Data.")
                    return
                self._print_if_verbose("TIMEOUT: Try again")
        raise RuntimeError("Failed to send segment after multiple attempts")

    def receive(self):
        bytes_received = 0
        data = bytearray()
        expected_sn = FIRST_SN
        while True:
            try:
                sn, payload = self._recv_segment()

                # TODO: refactor. En lugar de usar un ACK distinto de 0 y 1, 
                # podríamos agregar una flag en el header (seteada en 1 si es
                # el ultimo segmento) y comparar sn con la flag.
                if sn == FIN:
                    self._print_if_verbose("Reach End-Of-Data.")
                    self._send_ack(FIN)
                    return data

                if sn == expected_sn:
                    self._print_if_verbose(f"Expected SN {sn}")
                    data.extend(payload)
                    bytes_received += len(payload)
                    expected_sn = 1 - expected_sn
                else:
                    self._print_if_verbose(f"Duplicate SN {sn}, re-acked but not re-appended")
                self._send_ack(sn)
                self._print_if_verbose(f"Payload size: {len(payload)}")
                self._print_if_verbose(f"Total payload bytes received: {bytes_received}")
            except socket.timeout:
                self._print_if_verbose("TIMEOUT: Try again")
