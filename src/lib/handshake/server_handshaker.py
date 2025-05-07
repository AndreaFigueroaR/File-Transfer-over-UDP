import socket
from lib.handshake.serializer import *
TAM_BUFFER = 1024

STOP_ADN_WAIT = 'sw'
SELECTIVE_REPEAT = 'sr'
NUM_ATTEMPS = 10


class ServerHandshaker:
    def __init__(self, addr):
        self.client_addr = addr
        self.num_seq = 0

    def handshake(self, client_data, skt_peer):
        syn, client_num_seq, client_prot_type, client_app_metadata = MessgageSerializer.first_msg_from_bytes(
            client_data)
        if not syn:
            print("[Error]: recevie a message not expected at handshake, please retry")

        self._check_prot_type(client_prot_type)
        self._send_msg_2(skt_peer, client_num_seq)
        return client_prot_type, client_app_metadata

    def _send_msg_2(self, skt_peer, client_num_seq) -> int:
        packet = MessgageSerializer.second_msg_to_bytes(
            self.num_seq, client_num_seq)
        for _ in range(NUM_ATTEMPS):
            try:
                skt_peer.sendto(packet, self.client_addr)
                client_data, self.client_addr = skt_peer.recvfrom(TAM_BUFFER)
            except socket.timeout:
                continue

            if not MessgageSerializer._is_about_handhshake(
                    client_data):  # not syn
                return

            # if it is a corrupted message, it ask for the ack again
            _, ack = MessgageSerializer.third_msg_from_bytes(client_data)
            if self.num_seq == ack:
                return

        raise ConnectionError(
            "tried to reach the server several times without response")

    def _check_prot_type(self, client_prot_type):
        if not (client_prot_type ==
                STOP_ADN_WAIT or client_prot_type == SELECTIVE_REPEAT):
            raise ValueError(
                f"[Client] Invalid client protocol type, received: {client_prot_type}. Not a valid selection")
