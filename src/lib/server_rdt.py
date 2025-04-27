import socket
from handshake.server_handshaker import ServerHandshaker
from lib.selective_repeat import SelectiveRepeat
from stop_and_wait import StopAndWait

PROT_SR = "sr"


class ServerRDT:
    def __init__(self, addr):
        self.client_addr = addr
        self.peer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol = None
        self.client_num_seq = None
        self.num_seq = 0

    def meet_client(self, client_data, server_prot_type) -> str:
        handshaker = ServerHandshaker(self.client_addr, self.num_seq)
        self.client_num_seq, client_prot_type, app_data = handshaker.handshake(
            client_data, self.peer)
        self._check_prot_type(client_prot_type, server_prot_type)
        self.protocol = self._init_protocol(server_prot_type)
        return app_data

    def send(self, data):
        self.protocol.send(data)

    def receive(self):
        return self.protocol.recieve()

    def stop(self):
        self.protocol.stop()

    def _check_prot_type(client_prot_type, server_prot_type):
        if client_prot_type != server_prot_type:
            raise ValueError(
                f"Tipo de protocolo inválido: {client_prot_type}. Expected {server_prot_type}")

    def _init_protocol(self, prot_type):
        if prot_type == PROT_SR:
            return SelectiveRepeat(
                self.peer, self.num_seq, self.client_num_seq)
        return StopAndWait(self.peer, self.num_seq, self.client_num_seq)
