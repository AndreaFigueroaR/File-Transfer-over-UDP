import socket

TAM_BUFFER = 1024
TIME_OUT = 0.1

UPLOAD = 'U'
DOWNLOAD = 'D'
NUM_ATTEMPS = 10


class ClientHandshaker:
    def __init__(self, addr):
        self.srv_addr = addr
        self.num_seq = 0

    def handshake(self, client_type, client_prot_type, srv_file_name, skt):
        srv_num_seq = self._send_first_msg(
            skt, client_type, client_prot_type, srv_file_name)
        self._send_second_msg(skt, srv_num_seq)
        return self.srv_addr

    def _send_first_msg(
            self, skt, client_type, client_prot_type, srv_file_name):
        packet = self._formatted_client_data(
            client_type, client_prot_type, srv_file_name)
        srv_num_seq, ack = self._try_first_msg(skt, packet)
        while self.num_seq != int(ack):  # forwarding while its corrupted
            srv_num_seq, ack = self._try_first_msg(skt, packet)
            print(
                f"[Error]: ack received {ack}. Expected{self.num_seq}. Trying to connect the server again")
        return srv_num_seq

    def _send_second_msg(self, skt, srv_num_seq):
        skt.sendto(str(srv_num_seq).encode(), self.srv_addr)

    def _try_first_msg(self, skt, packet):
        for _ in range(NUM_ATTEMPS):
            try:
                skt.sendto(packet.encode(), self.srv_addr)
                data_handshake, self.srv_addr = skt.recvfrom(TAM_BUFFER)
            except socket.timeout:
                continue
            srv_num_seq, ack = data_handshake.decode().split("|", 1)
            return srv_num_seq, ack
        raise ConnectionError(
            "tried to reach the server several times without response")

    def _formatted_client_data(
            self, client_type, client_prot_type, srv_file_name) -> str:
        return f"{self.num_seq}|{client_prot_type}|{client_type}|{srv_file_name}"
