from lib.protocols.serializer import *
from typing import Tuple
import lib.debug as debug
from lib.protocols.config import *

class SerializerSW:
    @staticmethod
    def serialize_segment(segment_sn, data_segment,is_fin) -> bytes:
        syn_byte = Serializer.bool_to_byte(False)
        fin_byte = Serializer.bool_to_byte(is_fin)
        checksum_bytes = Serializer.get_checksum_data(data_segment)
        seq_num_byte = segment_sn.to_bytes(1, byteorder='big')
        
        segment = syn_byte + fin_byte + checksum_bytes + seq_num_byte + data_segment
        return segment
    
    @staticmethod
    def deserialize_segment(segment: bytes) -> Tuple[bool, int, bool, bytes]:
        is_fin = Serializer.byte_to_bool(segment[1:2])

        checksum_received = segment[2:6]
        seq_num = int.from_bytes(segment[6:SW_SEGMENT_HEADER_SIZE], byteorder='big')
        payload = segment[SW_SEGMENT_HEADER_SIZE:]

        checksum_calculated = Serializer.get_checksum_data(payload)
        if checksum_received != checksum_calculated:
            debug.log_warning(f"Checksum mismatch: {checksum_received} != {checksum_calculated}")
            return None
        return is_fin,seq_num, payload
    
    @staticmethod
    def deserialize_ack(ack_segment)->Tuple[bool,int]:
        is_fin = Serializer.byte_to_bool(ack_segment[1:SW_ACK_HEADER_SIZE])
        ack = int.from_bytes(ack_segment[SW_ACK_HEADER_SIZE:3], byteorder='big')
        return is_fin, ack
    
    @staticmethod
    def serialize_ack( ack, is_fin):
        syn_b = Serializer.bool_to_byte(False)
        is_fin_b = Serializer.bool_to_byte(is_fin)
        ack_b = ack.to_bytes(1, byteorder='big')

        return syn_b + is_fin_b + ack_b 

    



