from abc import ABC, abstractmethod

TIMEOUT = 1
TAM_BUFFER = 1024


class ProtocolARQ:

    def __init__(self, socket_peer, local_seq, remote_seq, remote_adress):
        print("local_seq: ", local_seq)
        print("remote_seq: ", remote_seq)
        self.socket = socket_peer
        # self.time_out.settimeout(TIMEOUT)
        self.local_seq = local_seq
        self.remote_seq = remote_seq
        # tupla con address y port de con quien me debería de estar comunicando
        self.adress = remote_adress
 
    @abstractmethod
    def _recv_segment():
        pass
    # No tiene mucho sentido el método unitario de _send_segment
    # si solo se envia 1 segmento enotnces no podríamos aplicar la
    # lógica de enviar varios consecutivamente (solo tedría sentido para stop
    # and wait)

    @abstractmethod
    def send(self, data: bytes):
        pass

    @abstractmethod
    def receive(self, total_size) -> bytearray:
        pass

    @abstractmethod
    def _send_segment(self, segment: bytes):
        pass

    @abstractmethod
    def stop(self):
        pass
