import socket

TAM_BUFFER = 1024
TIME_OUT = 0.1

CANT_ATTEMPS_FOR_SENDING_MSG = 10
TYPE_PROTOCOL_STOP_ADN_WAIT = 'sw'
TYPE_PROTOCOL_SELECTIVE_REPEAT = 'sr'

class ServerHandshaker:
    def __init__(self, addr, num_seq):
        self.client_addr = addr
        self.num_seq = num_seq

    def handshake(self, client_data, skt_peer):
        client_num_seq, client_prot_type, client_app_data = client_data.decode().split('|', 2)
        self._check_type_client(client_prot_type)
        packet = self._pkt_to_send(client_num_seq)
        self._send_handshake_msg(skt_peer, packet)
        return client_prot_type, client_app_data, client_num_seq

    def _send_handshake_msg(self, skt_peer, packet):
        ack = self._try_send_handshake_msg(skt_peer, packet)
        while ack != str(self.num_seq):  # forwarding while its corrupted
            ack = self._try_send_handshake_msg(skt_peer, packet)
            print(
                f"[Error]: ack received {ack}. Expected{self.num_seq}. Trying to connect the client again")

    def _try_send_handshake_msg(self, skt_peer, packet) -> str:
        for _ in range(CANT_ATTEMPS_FOR_SENDING_MSG):
            try:
                skt_peer.sendto(packet, self.client_addr)
                ack, self.client_addr = skt_peer.recvfrom(TAM_BUFFER)
            except socket.timeout:
                continue
            return ack.decode()
        print(f"[Error]: maximum number of attempts to send message was reached")

    def _pkt_to_send(self, client_num_seq) -> str:
        f"{self.num_seq}|{client_num_seq}".encode()

    def _check_type_client(type_prot_client):
        if not (type_prot_client ==
                TYPE_PROTOCOL_STOP_ADN_WAIT or type_prot_client == TYPE_PROTOCOL_SELECTIVE_REPEAT):
            raise ValueError(f"[Client] Invalid client protocol type, received: {type_prot_client}. Not a valid selection")
