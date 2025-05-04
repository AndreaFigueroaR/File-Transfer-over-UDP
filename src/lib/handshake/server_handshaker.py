import socket

TAM_BUFFER = 1024

STOP_ADN_WAIT = 'sw'
SELECTIVE_REPEAT = 'sr'
NUM_ATTEMPS = 10


class ServerHandshaker:
    def __init__(self, addr):
        self.client_addr = addr
        self.num_seq = 0

    def handshake(self, client_data, skt_peer):
        client_num_seq, client_prot_type, client_app_data = client_data.decode().split('|', 2)
        self._check_prot_type(client_prot_type)
        packet = self._pkt_to_send(client_num_seq)
        self._send_handshake_msg(skt_peer, packet)
        return client_prot_type, client_app_data

    def _send_handshake_msg(self, skt_peer, packet):
        ack = self._try_send_handshake_msg(skt_peer, packet)
        while ack != str(self.num_seq):  # forwarding while its corrupted
            ack = self._try_send_handshake_msg(skt_peer, packet)
            print(
                f"[Error]: ack received {ack}. Expected{self.num_seq}. Trying to connect the client again")

    def _try_send_handshake_msg(self, skt_peer, packet) -> str:
        for _ in range(NUM_ATTEMPS):
            try:
                skt_peer.sendto(packet, self.client_addr)
                ack, self.client_addr = skt_peer.recvfrom(TAM_BUFFER)
            except socket.timeout:
                continue
            return ack.decode()
        raise ConnectionError(
            "tried to reach the server several times without response")

    def _pkt_to_send(self, client_num_seq) -> str:
        return f"{self.num_seq}|{client_num_seq}".encode()

    def _check_prot_type(self, client_prot_type):
        if not (client_prot_type ==
                STOP_ADN_WAIT or client_prot_type == SELECTIVE_REPEAT):
            raise ValueError(
                f"[Client] Invalid client protocol type, received: {client_prot_type}. Not a valid selection")
