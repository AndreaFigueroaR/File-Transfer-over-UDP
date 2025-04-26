import socket

TAM_BUFFER = 1024
TIME_OUT = 0.1

TYPE_CLIENT_DOWNLOAD = 'D'
TYPE_CLIENT_UPLOAD = 'U'
class ServerHandshaker:
    def __init__(self, addr,num_seq):
        self.client_addr = addr
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt.timeout(TIME_OUT)
        self.num_seq = num_seq
    

    def handshake(self,client_data, skt_peer):
        client_num_seq,client_prot_type,client_app_data = client_data.decode().split('|',2) # 2 es la cantidad de splits en "client_num_seq| prot_type| file_path|client_type"
        
        if not (client_prot_type == TYPE_CLIENT_DOWNLOAD or self.type_client == TYPE_CLIENT_UPLOAD):
            raise ValueError(f"Tipo de cliente inválido: {self.type_client}")
        
        packet = self._pkt_to_send(client_num_seq)
        self._send_handshake_msg(skt_peer,packet)
        return client_prot_type, client_app_data, client_num_seq
    
    

    def _send_handshake_msg(self,skt_peer,packet):
        ack = self._try_send_handshake_msg(skt_peer,packet)
        while ack != str(self.num_seq):  # forwarding while its corrupted
            ack =  self._try_send_handshake_msg(skt_peer,packet)
            print(
                f"[Error]: ack received {ack}. Expected{self.num_seq}. Trying to connect the client again")

    def _try_send_handshake_msg(self, skt_peer, packet) -> str:
        skt_peer.sendto(packet,self.client_addr)
        try:
            ack, self.client_addr = skt_peer.recvfrom(TAM_BUFFER)
        except socket.timeout:
            self._try_send_handshake_msg(self, skt_peer, packet)
        return ack.decode()
    
    def _pkt_to_send(self, client_num_seq) ->str:
        f"{self.num_seq}|{client_num_seq}".encode()

