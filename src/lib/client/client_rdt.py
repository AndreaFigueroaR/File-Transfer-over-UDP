import socket
from lib.handshake.client_handshaker import ClientHandshaker
from lib.protocols.selective_repeat import SelectiveRepeat
from lib.protocols.stop_and_wait import StopAndWait

TIME_OUT = 0.1
PROT_SR = "sr"


class ClientRDT:
    def __init__(self, server_addr):
        self.srv_addr = server_addr
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt.settimeout(TIME_OUT)
        self.protocol = None
        self.srv_num_seq = None
        self.num_seq = 0

    def start(self, prot_type, client_type, srv_file_name, is_verbose) -> str:
        handshaker = ClientHandshaker(self.srv_addr, self.num_seq)
        self.srv_num_seq, self.srv_addr = handshaker.handshake(
            client_type, prot_type, srv_file_name, self.skt)
        self.protocol = self._init_protocol(prot_type, is_verbose)

    def send(self, data):
        self.protocol.send(data)

    def receive(self, sz) -> bytearray:
        return self.protocol.receive(sz)

    def stop(self):
        self.protocol.stop()

    def _init_protocol(self, prot_type, is_verbose):
        if prot_type == PROT_SR:
            return SelectiveRepeat(
                self.skt, self.num_seq, self.srv_num_seq, self.srv_addr, is_verbose)
        return StopAndWait(self.skt, self.num_seq,
                           self.srv_num_seq, self.srv_addr, is_verbose)
