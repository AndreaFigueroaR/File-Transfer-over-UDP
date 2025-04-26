import socket
import time
from abc import ABC, abstractmethod

TAM_BUFFER = 1024
TIME_OUT = 0.1

TYPE_CLIENT_DOWNLOAD ='D'
TYPE_CLIENT_UPLOAD ='U'

class ClientHandshaker:
    def __init__(self,args,type_client):
        self.foreign_addr = (args.host,args.port)
        self.protocol_type = args.protocol
        self.file_path = args.name
        self.num_seq = 0 ##creo que va en client
        self.serv_seq = None
        self.type_client = type_client

        if not (self.type_client == TYPE_CLIENT_DOWNLOAD or self.type_client == TYPE_CLIENT_UPLOAD):
            raise ValueError(f"Tipo de cliente inválido: {self.type_client}")


    def send_first_handshake_msg(self,skt):
        packet = self._formated_first_pkt()
        self.serv_seq, ack = self._try_first_handshake_msg(skt,packet)
        while int(ack) != self.num_seq:  # forwarding while its corrupted
            self.serv_seq, ack =  self._try_first_handshake_msg(skt,packet)
            print(
                f"[Error]: ack received {ack}. Expected{self.num_seq}. Trying to connect the server again")
        return

    # pre: you have be call send_first_handshake_msg before calling this
    def send_second_handshake_msg(self,skt):
        skt.sendto(str(self.serv_seq).encode(), self.foreign_addr)
        return self.num_seq
    

    def _try_first_handshake_msg(self, skt, packet):
        skt.sendto(packet.encode(),self.foreign_addr)
        try:
            data_handshake, self.foreign_addr  = skt.recvfrom(TAM_BUFFER)
        except socket.timeout:
            self._try_first_handshake_msg(self, skt, packet)
            time.sleep(1)#TODO: quitar

        serv_seq, ack = data_handshake.decode().split("|", 1)
        return (serv_seq, ack)


    def _formated_first_pkt(self) -> str:
        return f"{self.num_seq}|{self.type_client}|{self.protocol_type}|{self.file_path}" # por ejemplo 0|D|sr|hola.txt





    # @abstractmethod
    # def upload(self):
    #     pass
    
    # @abstractmethod
    # def download(self):
    #     pass

    # @abstractmethod
    # def recv_segment(self):
    #     pass
    
    # @abstractmethod
    # #[seq, ack, segment]
    # def send_segment(self, sock, addr, payload, lenght):
    #     pass
