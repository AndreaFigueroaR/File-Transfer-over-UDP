from protocol_arq import ProtocolARQ, TIMEOUT, TAM_BUFFER


class StopAndWait(ProtocolARQ):

    def send(self, data: bytes):
        # separar la data en segmentos
        for i in range(0, len(data)):
            segment = data[i:i + TAM_BUFFER]
            self._send_segment(segment)

    def _send_segment(slef, segment: bytes):
        while True:
            self.socket.sendto(segment)

            self.socket.reckfrom()

    def receive(self) -> bytes:

    def stop(self):
        self.socket.close()
