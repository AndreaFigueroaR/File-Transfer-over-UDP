from lib.protocol_arq import ProtocolARQ, TIMEOUT, TAM_BUFFER
import socket
# TODO: Cómo es que el mismo stop and wait determina su propio window size?

class StopAndWait(ProtocolARQ):

    # se recibe cualqueir tamaño
    def send(self, data: bytes):
        print("GAAAA")
        print(f"Len data:   {len(data)}")
        # separar la data en segmentos
        for i in range(0, len(data), TAM_BUFFER):
            # TODO: Verificar que no rompe si no se cumple con el TAM_BUFFER
            segment = data[i:i + TAM_BUFFER]
            self._send_segment(segment)

    # aqui se divide en tamaños fijos maximo

    # TODO : hacer parte del header de cada segmento el largo del payload
    # (aparte del numero de secuencia)
    def _send_segment(self, segment: bytes):
        seq_id_b = self.remote_seq.to_bytes(1, byteorder='big')
        pkt = seq_id_b + segment#[1 + TAMBUFFER]
        self.socket.sendto(pkt, self.adress)  # adress[IP:PORT]
        try:
            print("seneeeend")
            rcv_pkt, _ = self.socket.recvfrom(1)
            ack = int.from_bytes(rcv_pkt[:1], byteorder='big')

            print(ack)
            print(self.remote_seq)
            if ack != self.remote_seq:
                self._send_segment(segment)  # TODO: Agregar caso base
            else:
                self.remote_seq = 1 - self.remote_seq
        except socket.timeout:
            print("[Error]: Timeout")
            self._send_segment(segment)
            print("[Error]: Resended segment")
            # Aca si tenemos muchos timeouts podriamos cortar


    # Devuelve todo un paquete listo para que hagan file.wirte(bytearray)
    def receive(self, total_size) -> bytearray:
        print(f"[Info]: Receiving data desde {self.socket.getsockname()[1]}")
        buffer = bytearray()

        while True:#1024
            print("[receive] while true")
            try:
                packet, _ = self.socket.recvfrom(1 + TAM_BUFFER)  # +1 para el byte de secuencia     
                print(f"[Info]: Packet received : {packet} from {self.socket.getsockname()[1]}")
                #seq=packet[0]
               
                seq = int.from_bytes(packet[0], byteorder='big')#esta ya no es un int?? ->seq=packet[0]
                segment=packet[1:]

                if not segment:
                    break
                #MANEJAR CUANDO TERMINA
                    #if condicion para terminar:
                    #hanshake de despedida
                    
                print(seq)
                print(self.remote_seq)
                if seq==self.remote_seq:
                    buffer.extend(segment)
                    ack = seq.to_bytes(1, byteorder='big')#convierte el ack que me mandaron a bytes
                    self.socket.sendto(ack, self.adress)
                    #alternar el seq:
                    self.remote_seq = 1-self.remote_seq
                
                else:#timeout o perdida de paquete -> vuelvo a mndar ultimo
                    ack = (1-self.remote_seq).to_bytes(1, byteorder='big')                    
                    self.socket.sendto(ack, self.adress)
            
            except socket.timeout:  
                print("[Error]: Timeout receive")
                ack = (1-self.remote_seq).to_bytes(1, byteorder='big')                    
                self.socket.sendto(ack, self.adress)
                print("[Error]: Resended segment")


        return buffer


    def stop(self):  # TODO: maybe un try? arriba se espera se haga seguramente (creo)
        self.socket.close()
