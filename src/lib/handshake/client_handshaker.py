import socket
from lib.handshake.serializer import MessageSerializer
from lib.utils.timeout_estimator import reconsider_timeout

TAM_BUFFER = 1024

UPLOAD = 'U'
DOWNLOAD = 'D'
NUM_ATTEMPS_HANDSHAKE = 15

class ClientHandshaker:
    def __init__(self, addr):
        self.srv_addr = addr
        self.num_seq = 0

    def handshake(self, client_type, client_prot_type, srv_file_name, skt):
        app_metadata = client_type + srv_file_name
        srv_num_seq = self._send_msg_1(skt, client_prot_type, app_metadata)

        if client_type == UPLOAD:
            self._send_innocent_mgs_3(skt, srv_num_seq)
        else:
            self._send_msg_3(skt, srv_num_seq)
        return self.srv_addr

    def _send_innocent_mgs_3(self, skt, srv_num_seq):
        packet = MessageSerializer.third_msg_to_bytes(srv_num_seq)
        skt.sendto(packet, self.srv_addr)

    def _send_msg_3(self, skt, srv_num_seq):
        packet = MessageSerializer.third_msg_to_bytes(srv_num_seq)

        for _ in range(NUM_ATTEMPS_HANDSHAKE):
            try:
                skt.sendto(packet, self.srv_addr)
                data, self.srv_addr = skt.recvfrom(TAM_BUFFER)

                if not MessageSerializer._is_about_handhshake(data):
                    return

            except socket.timeout:
                reconsider_timeout(skt)
                continue
        raise ConnectionError(
            "tried to reach the server several times without response")

    def _send_msg_1(self, skt, client_prot_type, app_metadata) -> int:
        packet = MessageSerializer.first_msg_to_bytes(
            self.num_seq, client_prot_type, app_metadata)

        for _ in range(NUM_ATTEMPS_HANDSHAKE):
            try:
                skt.sendto(packet, self.srv_addr)
                data_handshake, self.srv_addr = skt.recvfrom(TAM_BUFFER)
            except socket.timeout:
                reconsider_timeout(skt)
                continue
            if not MessageSerializer._is_about_handhshake(data_handshake):
                # This should not happen
                assert False, "[Error]: message not expected at handshake"

            srv_num_seq, ack = MessageSerializer.second_msg_from_bytes(
                data_handshake)

            if self.num_seq == ack:
                return srv_num_seq

        raise ConnectionError(
            "tried to reach the server several times without response")
