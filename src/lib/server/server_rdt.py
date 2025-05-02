import socket
from lib.handshake.server_handshaker import ServerHandshaker
from lib.protocols.selective_repeat import SelectiveRepeat
from lib.protocols.stop_and_wait import StopAndWait

TIME_OUT = 0.1
PROT_SR = "sr"


class ServerRDT:
    def __init__(self, addr):
        self.client_addr = addr
        self.peer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.peer.settimeout(TIME_OUT)
        self.protocol = None
        self.client_num_seq = None
        self.num_seq = 0

    def meet_client(self, client_data, server_prot_type, is_verbose) -> str:
        handshaker = ServerHandshaker(self.client_addr, self.num_seq)
        self.client_num_seq, client_prot_type, app_data = handshaker.handshake(
            client_data, self.peer)
        self._check_prot_type(client_prot_type, server_prot_type)
        self.protocol = self._init_protocol(server_prot_type, is_verbose)
        return app_data

    def send(self, data):
        self.protocol.send(data)

    def receive(self, sz) -> bytearray:
        return self.protocol.receive(sz)

    def stop(self):
        self.protocol.stop()

    def _init_protocol(self, prot_type, is_verbose):
        if prot_type == PROT_SR:
            return SelectiveRepeat(self.peer, self.client_num_seq, self.client_addr, is_verbose)
        return StopAndWait(self.peer, self.client_num_seq, self.client_addr, is_verbose)

    def _check_prot_type(self, client_prot_type, server_prot_type):
        if client_prot_type != server_prot_type:
            raise ValueError(
                f"Invalid protocol type: {client_prot_type}. Expected {server_prot_type}")
