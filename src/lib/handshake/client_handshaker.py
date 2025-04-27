import socket

TAM_BUFFER = 1024
TIME_OUT = 0.1

UPLOAD = 'U'
DOWNLOAD = 'D'
NUM_ATTEMPS = 10


class ClientHandshaker:
    def __init__(self, addr, num_seq):
        self.srv_addr = addr
        self.num_seq = num_seq

    def handshake(self, client_type, client_prot_type, file_path, srv_skt):
        srv_num_seq = self._send_first_handshake_msg(
            srv_skt, client_type, client_prot_type, file_path)
        self._send_second_handshake_msg(srv_skt, srv_num_seq)
        return srv_num_seq

    def _send_first_handshake_msg(
            self, srv_skt, client_type, client_prot_type, file_path):
        packet = self._formatted_client_info(
            client_type, client_prot_type, file_path)
        srv_num_seq, ack = self._try_first_handshake_msg(srv_skt, packet)
        while self.num_seq != int(ack):  # forwarding while its corrupted
            srv_num_seq, ack = self._try_first_handshake_msg(srv_skt, packet)
            print(
                f"[Error]: ack received {ack}. Expected{self.num_seq}. Trying to connect the server again")
        return srv_num_seq

    def _send_second_handshake_msg(self, srv_skt, srv_num_seq):
        srv_skt.sendto(str(srv_num_seq).encode(), self.srv_addr)

    def _try_first_handshake_msg(self, srv_skt, packet):
        for _ in range(NUM_ATTEMPS):
            try:
                srv_skt.sendto(packet.encode(), self.srv_addr)
                data_handshake, self.srv_addr = srv_skt.recvfrom(TAM_BUFFER)
            except socket.timeout:
                continue
            srv_num_seq, ack = data_handshake.decode().split("|", 1)
            return srv_num_seq, ack
        raise ConnectionError("Maximum number of handshake attempts reached")

    def _formatted_client_info(
            self, client_type, client_prot_type, file_path) -> str:
        return f"{self.num_seq}|{client_type}|{client_prot_type}|{file_path}"
