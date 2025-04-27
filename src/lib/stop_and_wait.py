from protocol_arq import ProtocolARQ, TIMEOUT, TAM_BUFFER

# TODO: Cómo es que el mismo stop and wait determina su propio window size?


class StopAndWait(ProtocolARQ):

    # se recibe cualqueir tamaño
    def send(self, data: bytes):
        # separar la data en segmentos
        for i in range(0, len(data), TAM_BUFFER):
            # Verificar que no rompe si no se cumple con el TAM_BUFFER
            segment = data[i:i + TAM_BUFFER]
            self._send_segment(segment)

    # aqui se divide en tamaños fijos maximo

    # TODO : hacer parte del header de cada segmento el largo del payload
    # (aparte del numero de secuencia)
    def _send_segment(self, segment: bytes):
        seq_id_b = self.seq_local.to_bytes(1, byteorder='big')
        pkt = seq_id_b + segment
        self.socket.sendto(pkt, self.adress)  # adress[IP:PORT]
        try:
            rcv_pkt, _ = self.socket.rcvfrom(1)
            ack = int.from_bytes(rcv_pkt[:1], byteorder='big')

            if ack != self.seq_local:
                self._send_segment(segment)  # TODO: Agregar caso base
            else:
                self.seq_local += 1
                self.seq_remote = ack
        except self.socket.timeout:
            self._send_segment(segment)
            # Aca si tenemos muchos timeouts podriamos cortar

    def receive(self, total_size) -> bytearray:
        # No debo salir de aquí hasta que se reciba la cantidad de bytes que se indica
        # creo que debería recibir
        received = 0
        ack = 0
        buffer = bytearray()
        self.socket.settimeout(TIMEOUT)
        while received < total_size:
            # el tamaño de lo máximo que queremos recibir
            data, address = self.socket.recvfrom(total_size - received)
            buffer.extend(data)
            pass

    def stop(self):  # TODO: maybe un try? arriba se espera se haga seguramente (creo)
        self.socket.close()
