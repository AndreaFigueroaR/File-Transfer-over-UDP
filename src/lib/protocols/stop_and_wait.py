from lib.protocols.protocol_arq import *
from typing import Optional, Tuple
import socket
import lib.debug as debug
from lib.protocols.serializer_SW import *
from lib.protocols.config import *

class StopAndWait(ProtocolARQ):
    def _recv_ack(self) -> Tuple[bool,int]:
        segment, _ = self.socket.recvfrom(SW_ACK_SIZE + SW_ACK_HEADER_SIZE)
        return SerializerSW.deserialize_ack(segment)
        
        
    def _send_ack(self, ack, is_fin=False):
        ack_segment = SerializerSW.serialize_ack(ack,is_fin)
        self.socket.sendto(ack_segment, self.address)


    def _send_segment(self, segment_sn, data_segment: bytes,is_fin):
        debug.log(f"{IND}{DELIM}")
        debug.log(f"{IND}Segment size to send: {SW_SEGMENT_HEADER_SIZE  + len(data_segment)}")
        segment = SerializerSW.serialize_segment(segment_sn, data_segment,is_fin)
        self.socket.sendto(segment, self.address)
    

    def _recv_segment(self) -> Optional[Tuple[bool,int, bytes]]:
        segment, _ = self.socket.recvfrom(SW_SEGMENT_HEADER_SIZE  + DATA_CHUNK_SIZE)
        if Serializer.is_about_handhshake(segment):
            return None
        debug.log(DELIM)
        debug.log(f"Total segment size recieved: {len(segment)}")
        return SerializerSW.deserialize_segment(segment)


    def send(self, data):
        debug.log(f"Data size to send: {len(data)}")
        data_chunks = self._split_data(data)
        sn = FIRST_SN
        for chunk in data_chunks:
            self._send_data_chunk(sn, chunk)
            sn = 1 - sn
        self._send_data_chunk(sn, bytes(), is_my_fin=True)


    def _send_data_chunk(self, sn, chunk,is_my_fin=False):
        for _ in range(NUM_ATTEMPS):
            try:
                self._send_segment(sn, chunk,is_my_fin)
                is_receiver_fin, ack = self._recv_ack()
                if ack == sn:
                    debug.log(f"{IND}Received expected ACK: {ack}")
                    return
                if is_receiver_fin:
                    debug.log("Reach End-Of-Data.")
                    return
                debug.log_warning(f"{IND}Received unexpected ACK: {ack}")
            except socket.timeout:
                if is_my_fin:
                    debug.log("[MY FIN] Reach End-Of-Data.")
                    return
                debug.log_error("TIMEOUT: Try again")
        raise RuntimeError("Failed to send segment after multiple attempts")
    

    def receive(self):
        bytes_received = 0
        data = bytearray()
        expected_sn = FIRST_SN
        attemps = 0
        while attemps < NUM_ATTEMPS // 2:
            try:
                segment = self._recv_segment()
                if segment is None:
                    continue
                is_fin, sn, payload = segment

                attemps = 0

                if is_fin:
                    debug.log("Reach End-Of-Data.")
                    self._send_ack(sn, is_fin=True)
                    return data

                if sn == expected_sn:
                    debug.log(f"Expected SN {sn}")
                    data.extend(payload)
                    bytes_received += len(payload)
                    expected_sn = 1 - expected_sn
                else:
                    debug.log_warning(f"Duplicate SN {sn}, re-acked but not re-appended")
                self._send_ack(sn)
                debug.log(f"Payload size: {len(payload)}")
                debug.log(f"Total payload bytes received: {bytes_received}")
            except socket.timeout:
                attemps += 1
                debug.log("TIMEOUT: Try again")
        return data
    