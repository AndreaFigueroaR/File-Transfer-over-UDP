import socket
from lib.handshake.client_handshaker import ClientHandshaker
from lib.protocols.selective_repeat import SelectiveRepeat
from lib.protocols.stop_and_wait import StopAndWait

TIME_OUT = 0.01
PROT_SR = "sr"


class ClientRDT:
    def __init__(self, server_addr):
        self.srv_addr = server_addr
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt.settimeout(TIME_OUT)
        self.protocol = None

    def stablish_connection(self, prot_type, client_type, srv_file_name):
        handshaker = ClientHandshaker(self.srv_addr)
        self.srv_addr = handshaker.handshake(
            client_type, prot_type, srv_file_name, self.skt)
        self.protocol = self._init_protocol(prot_type)

    def send(self, data):
        self.protocol.send(data)

    def receive(self) -> bytearray:
        return self.protocol.receive()

    def stop(self):
        self.skt.close()

    def _init_protocol(self, prot_type):
        if prot_type == PROT_SR:
            return SelectiveRepeat(self.skt, self.srv_addr)
        return StopAndWait(self.skt, self.srv_addr)
