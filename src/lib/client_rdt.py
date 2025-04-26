import socket
from handshake.client_handshaker import ClientHandshaker
from lib.selective_repeat import SelectiveRepeat
from stop_and_wait import StopAndWait

PROT_SR = "sr"

class ClientRDT:
    def __init__(self, server_addr):
        self.srv_addr = server_addr
        self.srv_skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.protocol = None
        self.srv_num_seq = None
        self.num_seq = 0

    def start(self, prot_type, client_type, file_path) -> str:
        handshaker = ClientHandshaker(self.srv_addr, self.num_seq)
        self.srv_num_seq = handshaker.handshake(client_type, prot_type, file_path, self.srv_skt)
        self.protocol = self._init_protocol(prot_type)

    def send(self, data):
        self.protocol.send(data)

    def receive(self):
        return self.protocol.recieve()

    def stop(self):
        self.protocol.stop()

    def _init_protocol(self, prot_type):
        if prot_type == PROT_SR:
            return SelectiveRepeat(self.srv_skt, self.num_seq, self.srv_num_seq)
        return StopAndWait(self.srv_skt, self.num_seq, self.srv_num_seq)
