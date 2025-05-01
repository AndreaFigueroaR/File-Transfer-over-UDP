from lib.protocols.protocol_arq import *
import time
import socket

WIN_SIZE = 4

class SelectiveRepeat(ProtocolARQ):

    def __init__(self, socket_peer, local_seq, remote_seq, remote_adress):
        super().__init__(socket_peer, local_seq, remote_seq, remote_adress)
        self.win_size = WIN_SIZE  # calcular?
        self.ack_buffer = set()
        self.pkt_buffer = {}
        self.sent_timers = {}
        pass

    def _split_data(self, data: bytes):
        result = []
        for i in range(0, len(data), TAM_BUFFER):
            result.append(data[i:i + TAM_BUFFER])
        return result

    def expired_pkts(self):
        current_time = time.time()
        expired = [pkt for pkt, time in self.sent_timers.items() if time + TIMEOUT <= current_time]
        
        for expired_pkt in expired:
            del self.sent_timers[expired_pkt]

        return expired

    def send(self, data: bytes):        
        current_seq = 0

        if len(data) == 0:
            # enviando ack de despedida
            ack = current_seq.to_bytes(1, byteorder='big')
            self.socket.sendto(ack, self.adress)
            return

        packages = self._split_data(data) # divido la data en paquetes

        while current_seq < len(packages):
            # envio aquellos paquetes dentro de la window para los cuales: no estoy esperando ack y no he recibido ack
            for pkt_id in range(current_seq, min(current_seq + WIN_SIZE, len(packages))):
                if pkt_id in self.sent_timers or pkt_id in self.ack_buffer:
                    continue
                print(f"enviando pkt: {pkt_id}")
                self._send_seq_segment(pkt_id, packages[pkt_id])                

            print("espero recibir ack")
            rcv_pkt, _ = self.socket.recvfrom(1)
            ack = int.from_bytes(rcv_pkt[:1], byteorder='big')
            print("recibo ack:", ack)
            
            if ack == current_seq: # recibimos el ack esperado, deslizamos la ventana
                current_seq += 1
                while current_seq in self.ack_buffer:
                    self.ack_buffer.remove(current_seq)
                    current_seq += 1
            else: # recibimos otro ack, lo almacenamos
                self.ack_buffer.add(ack)
                print(f"no recibi el ack esperado, almaceno en buffer (ack: {ack})")

            del self.sent_timers[ack]

            # reenviar paquetes expirados
            for expired_pkt_id in self.expired_pkts():
                print("reenvio paquete expirado:", expired_pkt_id)
                self._send_seq_segment(expired_pkt_id, packages[expired_pkt_id])

    def _send_seq_segment(self, pkt_id, segment: bytes):
        seq_id_b = pkt_id.to_bytes(1, byteorder='big')
        pkt = seq_id_b + segment  # [1 + TAMBUFFER]
        self.socket.sendto(pkt, self.adress)
        self.sent_timers[pkt_id] = time.time() # establezco un timeout para el recibimiento del ack

    def receive(self, total_size) -> bytearray:
        expected_seq = 0
        buffer = bytearray()
        bytes_received = 0

        least_pkt_buffered = -1
        must_end = False
        while bytes_received < total_size:
            try:
                print("esperando recibir")
                packet, _ = self.socket.recvfrom(1 + TAM_BUFFER)
                seq = int.from_bytes(packet[:1], byteorder='big')
                payload = packet[1:]

                # recibimos el paquete esperado
                if seq == expected_seq:
                    print(f"Leo en payload:   {len(payload)}")
                    buffer.extend(payload)
                    bytes_received += len(payload)
                    
                    # ademas el paquete esperado era el ultimo
                    if len(payload) < TAM_BUFFER:
                        must_end = True        
                    else:
                        # deslizamos la ventana
                        expected_seq += 1
                        while expected_seq in self.pkt_buffer:
                            buffer.extend(self.pkt_buffer.pop(expected_seq))

                            if expected_seq == least_pkt_buffered: # Llegamos al ultimo paquete (que teniamos bufereado)
                                must_end = True

                            expected_seq += 1         

                else: # recibimos otro paquete, lo almacenamos
                    print(f"no recibi el pkt esperado, almaceno en buffer (pkt: {seq})")
                    self.pkt_buffer[seq] = payload
                    if len(payload) < TAM_BUFFER:
                        least_pkt_buffered = seq

                ack = seq.to_bytes(1, byteorder='big')
                self.socket.sendto(ack, self.adress)
                print("envio ack:", seq)

                if must_end:
                    return buffer                      

            except socket.timeout:
                print("[Error]: Timeout receive")
                ack = (1 - self.local_seq).to_bytes(1, byteorder='big')
                self.socket.sendto(ack, self.adress)
        
        return buffer


    def _send_segment(self, segment):
        pass
    def _recv_segment(self):
        pass

    def _formated_first_pkt_client(name, type_client, seq) -> str:
        return f"{seq}|{type_client}|sr|{name}"

    def stop(self):
        self.socket.close()
