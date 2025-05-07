import socket
from lib.handshake.server_handshaker import ServerHandshaker
from lib.protocols.selective_repeat import SelectiveRepeat
from lib.protocols.stop_and_wait import StopAndWait

TIME_OUT = 0.01
PROT_SR = "sr"


class ServerRDT:
    def __init__(self, addr):
        self.client_addr = addr
        self.peer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.peer.settimeout(TIME_OUT)
        self.protocol = None

    def meet_client(self, client_data, prot_type) -> str:
        handshaker = ServerHandshaker(self.client_addr)
        client_prot_type, app_data = handshaker.handshake(
            client_data, self.peer)
        self._check_prot_type(client_prot_type, prot_type)
        self.protocol = self._init_protocol(prot_type)
        return app_data

    def send(self, data):
        self.protocol.send(data)

    def receive(self) -> bytearray:
        return self.protocol.receive()

    def stop(self):
        self.peer.close()

    def _init_protocol(self, prot_type):
        if prot_type == PROT_SR:
            return SelectiveRepeat(self.peer, self.client_addr)
        return StopAndWait(self.peer, self.client_addr)

    def _check_prot_type(self, client_prot_type, prot_type):
        if client_prot_type != prot_type:
            raise ValueError(
                f"Invalid protocol type: {client_prot_type}. Expected {prot_type}")
