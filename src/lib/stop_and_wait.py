from lib.protocol_arq import ProtocolARQ, TIMEOUT, TAM_BUFFER
import socket
# TODO: Cómo es que el mismo stop and wait determina su propio window size?
FIN_SEQUENCE = b'\xFE\xFD\xFC'


class StopAndWait(ProtocolARQ):
    # se recibe cualqueir tamaño
    def send(self, data: bytes):
        print(f"Len data:   {len(data)}")
        if len(data) == 0:
            #enviando ack de despedida
            ack = self.remote_seq.to_bytes(1, byteorder='big')
            self.socket.sendto(ack, self.adress)
            self.remote_seq = 1 - self.remote_seq
            return
        for i in range(0, len(data), TAM_BUFFER):
            # TODO: Verificar que no rompe si no se cumple con el TAM_BUFFER
            segment = data[i:i + TAM_BUFFER]
            self._send_segment(segment)

    # TODO : hacer parte del header de cada segmento el largo del payload
    # (aparte del numero de secuencia)
    def _send_segment(self, segment: bytes):
        seq_id_b = self.remote_seq.to_bytes(1, byteorder='big')
        pkt = seq_id_b + segment  # [1 + TAMBUFFER]
        self.socket.sendto(pkt, self.adress)

        try:
            print("try enviar segmento")
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

    def receive(self, total_size) -> bytearray:
        buffer = bytearray()
        bytes_received = 0

        while bytes_received < total_size:
            try:
                packet, _ = self.socket.recvfrom(1 + TAM_BUFFER)
                seq = int.from_bytes(packet[0:1], byteorder='big')
                payload = packet[1:]

                if seq == self.remote_seq:
                    print(f"Leo en payload:   {len(payload)}")
                    buffer.extend(payload)
                    bytes_received += len(payload)
                    ack = seq.to_bytes(1, byteorder='big')
                    self.socket.sendto(ack, self.adress)
                    self.remote_seq = 1 - self.remote_seq
                    if len(payload)<TAM_BUFFER:
                        return buffer
                else:
                    print("No existen los erroes. Me verás cuando no uses tu misma ip c:")
                    # caso loss: reenviar último paquete
                    ack = (1 - self.remote_seq).to_bytes(1, byteorder='big')
                    self.socket.sendto(ack, self.adress)

            except socket.timeout:
                print("[Error]: Timeout receive")
                ack = (1 - self.remote_seq).to_bytes(1, byteorder='big')
                self.socket.sendto(ack, self.adress)

        return buffer

    def stop(self):  # TODO: maybe un try? arriba se espera se haga seguramente (creo)
        self.socket.close()
