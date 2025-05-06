from lib.protocols.protocol_arq import *
import socket

NUM_ATTEMPS = 10
FIRST_SN = 0
FIN = 2

class StopAndWait(ProtocolARQ):
    def send(self, data):
        self._print_if_verbose(f"Data size to send: {len(data)}")
        data_chunks = self._split_data(data)
        sn = FIRST_SN
        for chunk in data_chunks:
            self._send_data_chunk(sn, chunk)
            sn = 1 - sn

        #TODO: Creo que es lo mismo llamar a 
        # self._send_segment(sn, bytes(), is_my_fin=True)
        # porque el receiver igual permitiría rendirse a que no se reciba después de varios intentos
        self._send_data_chunk(sn, bytes(), is_my_fin=True)


    def _send_segment(self, segment_sn, data_segment: bytes,is_fin):
        self._print_if_verbose(f"{IND}{DELIM}")
        self._print_if_verbose(f"{IND}Segment size to send: {1 + len(data_segment)}")
        
        seq_num_byte = segment_sn.to_bytes(1, byteorder='big')
        fin_byte = self._bool_to_byte(is_fin)
        segment = seq_num_byte + fin_byte +data_segment
        self.socket.sendto(segment, self.address)

    def _send_data_chunk(self, sn, chunk,is_my_fin=False):
        for _ in range(NUM_ATTEMPS):
            try:
                self._send_segment(sn, chunk,is_my_fin)

                is_receiver_fin, ack = self._recv_ack()
                if ack == sn:
                    self._print_if_verbose(f"{IND}Received expected ACK: {ack}")
                    return
                if is_receiver_fin:
                    self._print_if_verbose("Reach End-Of-Data.")
                    return
                self._print_if_verbose(f"{IND}Received unexpected ACK: {ack}")
            except socket.timeout:
                if is_my_fin:
                    self._print_if_verbose("Reach End-Of-Data.")
                    return
                self._print_if_verbose("TIMEOUT: Try again")
        raise RuntimeError("Failed to send segment after multiple attempts")

    def receive(self):
        bytes_received = 0
        data = bytearray()
        expected_sn = FIRST_SN
        attemps = 0
        while attemps < NUM_ATTEMPS // 2:
            try:
                sn, is_fin, payload = self._recv_segment()
                attemps = 0

                if is_fin:
                    self._print_if_verbose("Reach End-Of-Data.")
                    self._send_ack(sn, is_fin=True)
                    return data

                if sn == expected_sn:
                    self._print_if_verbose(f"Expected SN {sn}")
                    data.extend(payload)
                    bytes_received += len(payload)
                    expected_sn = 1 - expected_sn
                else:
                    self._print_if_verbose(f"Duplicate SN {sn}, re-acked but not re-appended")
                self._send_ack(sn)
                self._print_if_verbose(f"Payload size: {len(payload)}")
                self._print_if_verbose(f"Total payload bytes received: {bytes_received}")
            except socket.timeout:
                attemps += 1
                self._print_if_verbose("TIMEOUT: Try again")
        return data
    



    def _recv_segment(self):
        segment, _ = self.socket.recvfrom(2 + DATA_CHUNK_SIZE)
        seq_num = int.from_bytes(segment[0:1], byteorder='big')
        is_fin = self._byte_to_bool(segment[1:2])
        payload = segment[2:]
        
        self._print_if_verbose(DELIM)
        self._print_if_verbose(f"Segment size recieved: {len(segment)}")
        return seq_num, is_fin, payload
    

    def _recv_ack(self):
        segment, _ = self.socket.recvfrom(2)
        is_fin = self._byte_to_bool(segment[0:1])
        ack = int.from_bytes(segment[1:2], byteorder='big')
        return is_fin, ack
    

    def _send_ack(self, ack, is_fin=False):
        ack_b = ack.to_bytes(1, byteorder='big')
        is_fin_b = self._bool_to_byte(is_fin)
        segment = is_fin_b + ack_b 
        self.socket.sendto(segment, self.address)