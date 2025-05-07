from lib.protocols.protocol_arq import *
import time
import socket
from lib import debug
from lib.protocols.serializer import Serializer
from lib.protocols.config import *


class SelectiveRepeat(ProtocolARQ):
    def __init__(self, socket, remote_address):
        super().__init__(socket, remote_address)
        self.pkt_id = 0

    def _send_segment_sr(self, segment_sn, pkt_id, data_segment: bytes):
        debug.log(f"{IND}{DELIM}")
        debug.log(
            f"{IND}Segment size to send: {SR_SEGMENT_HEADER_SIZE + len(data_segment)}")

        syn_byte = Serializer.bool_to_byte(False)
        checksum_bytes = Serializer.get_checksum_data(data_segment)
        seq_num_byte = segment_sn.to_bytes(1, byteorder='big')
        pkt_id_byte = pkt_id.to_bytes(2, byteorder='big')
        segment = syn_byte + checksum_bytes + seq_num_byte + pkt_id_byte + data_segment
        self.socket.sendto(segment, self.address)

    def _recv_ack_sr(self):
        segment, _ = self.socket.recvfrom(4)
        ack = int.from_bytes(segment[1:2], byteorder='big')
        pkt_id = int.from_bytes(segment[2:4], byteorder='big')
        return ack, pkt_id

    def send(self, data: bytes):
        current_sn = 0

        debug.log(f"Data size to send: {len(data)}")

        data_segments = self._split_data(data)
        data_segments.append(bytes())  # Agrego el final (segment vacio)
        ack_buffer = set()
        win_size = self._set_win_size(len(data_segments))
        timers = {}
        total_sent = 0
        attempts = 0
        while current_sn < len(data_segments):
            # Send segments within the window for which:
            # I'm not waiting for an ACK and haven't received an ACK
            win_end = min(current_sn + win_size, len(data_segments))
            for sn in range(current_sn, win_end):
                if sn in timers or sn in ack_buffer:
                    continue
                self._send_segment_sr(sn, self.pkt_id, data_segments[sn])
                timers[sn] = time.time()

            try:
                ack, ack_pkt_id = self._recv_ack_sr()
                attempts = 0
                debug.log(f"{IND}ACK expected: {current_sn}")
                debug.log(f"{IND}ACK received: {ack}")

                if ack_pkt_id < self.pkt_id:
                    continue

                if ack < current_sn:
                    debug.log_warning(f"{IND}Received duplicated ACK.")
                elif ack > current_sn:
                    ack_buffer.add(ack)
                    debug.log_warning(
                        f"{IND}Received out of order ACK. Buffered.")
                    total_sent += len(data_segments[ack])
                    del timers[ack]
                else:
                    debug.log(f"{IND}Received expected ACK.")
                    current_sn = self._update_current_sn(ack, ack_buffer)
                    total_sent += len(data_segments[ack])
                    del timers[ack]
            except socket.timeout:
                if current_sn == len(data_segments) - 1:
                    attempts += 1
                    if (attempts == NUM_ATTEMPS):
                        debug.log_warning(
                            f"{IND}[TIMEOUT] Esperando ack de FIN ({current_sn})")
                        break
                debug.log_warning(
                    f"{IND}[TIMEOUT] Esperando ack ({current_sn})")

            debug.log("Reviso timout de paquetes eviados")
            # Resend expired segments
            for sn in list(timers):
                if timers[sn] + TIMEOUT <= time.time():
                    debug.log(f"{IND}Resending expired segment with ACK {sn}.")
                    self._send_segment_sr(sn, self.pkt_id, data_segments[sn])
                    timers[sn] = time.time()
        self.pkt_id += 1
        debug.log(f"TOTAL SENT: {total_sent}")

    def _recv_segment_sr(self):
        # SYN, CHECKSUM, SEQ_NUM, PKT_ID, PAYLOAD
        segment, _ = self.socket.recvfrom(
            SR_SEGMENT_HEADER_SIZE + DATA_SEGMENT_SIZE)

        if Serializer.is_about_handhshake(segment):
            return None

        # Segment deserialization
        checksum_received = segment[1:5]
        seq_num = int.from_bytes(segment[5:6], byteorder='big')
        pkt_id = int.from_bytes(segment[6:8], byteorder='big')
        payload = segment[8:]

        checksum_calculated = Serializer.get_checksum_data(payload)
        if checksum_received != checksum_calculated:
            debug.log_warning(
                f"Checksum mismatch: {checksum_received} != {checksum_calculated}")
            return None

        debug.log(DELIM)
        debug.log(f"{IND}Segment size recieved: {len(segment)}")
        return seq_num, pkt_id, payload

    def receive(self) -> bytearray:
        expected_sn = 0
        segments_buffer = {}
        data = bytearray()

        end_segment_buffered = -1
        attempts = 0
        while attempts < NUM_ATTEMPS:
            try:
                segment = self._recv_segment_sr()
                if segment is None:
                    continue
                seq_num, pkt_id, payload = segment

                # attempts = 0
                if self.pkt_id != pkt_id:
                    self._send_ack_sr(seq_num, pkt_id)
                    debug.log_warning(
                        f"{IND}ME LLEGO UN PAQUETE ANTERIOR, CURRENT_PKG: {self.pkt_id}. REC > PKG:{pkt_id}, SEQ:{seq_num}, LEN_PAYLOAD: {len(payload)}")
                    continue

                debug.log(f"{IND}Sequence number expected: {expected_sn}")
                debug.log(f"{IND}Sequence number received: {seq_num}")

                if seq_num < expected_sn:
                    debug.log_warning(
                        f"{IND}Received duplicated sequence number.")
                    self._send_ack_sr(seq_num, pkt_id)
                elif seq_num > expected_sn:
                    if (seq_num, self.pkt_id) not in segments_buffer:
                        segments_buffer[(seq_num, self.pkt_id)] = payload
                        if len(payload) == 0:
                            end_segment_buffered = seq_num
                    debug.log_warning(
                        f"{IND}Received out of order sequence number. Buffered (if was not).")
                    self._send_ack_sr(seq_num, pkt_id)
                else:
                    debug.log(f"{IND}Received expected sequence number.")
                    data.extend(payload)
                    self._send_ack_sr(seq_num, pkt_id)

                    if len(payload) == 0:
                        self.pkt_id += 1
                        return data

                    # Store consecutive segments that were in the buffer and
                    # move forward
                    expected_sn = seq_num + 1
                    while (expected_sn, self.pkt_id) in segments_buffer:
                        data.extend(
                            segments_buffer.pop(
                                (expected_sn, self.pkt_id)))
                        if expected_sn == end_segment_buffered:
                            self.pkt_id += 1
                            return data
                        expected_sn += 1
            except socket.timeout:
                debug.log_error(f"{IND}[ERROR]: Timeout")
                attempts += 1

        debug.log_warning(f"{IND}CORTO POR ATTEMPTS")
        self.pkt_id += 1
        return data

    def _send_ack_sr(self, ack, pkt_id):
        syn_b = Serializer.bool_to_byte(False)
        ack_b = ack.to_bytes(1, byteorder='big')
        pkt_id_b = pkt_id.to_bytes(2, byteorder='big')
        self.socket.sendto(syn_b + ack_b + pkt_id_b, self.address)

    def _set_win_size(self, num_segments):
        return min(MAX_WIN_SIZE, num_segments)
        # half = num_segments // 2
        # return min(MAX_WIN_SIZE, max(1, half))

    def _update_current_sn(self, ack_received, ack_buffer):
        current_sn = ack_received + 1
        while current_sn in ack_buffer:
            ack_buffer.remove(current_sn)
            current_sn += 1
        return current_sn

    def _get_expired_segments_sn(self, timers):
        current_time = time.time()

        expired_segments_sn = []
        for segment_sn, segment_time in timers.items():
            if segment_time + TIMEOUT <= current_time:
                expired_segments_sn.append(segment_sn)

        for exp in expired_segments_sn:
            del timers[exp]

        return expired_segments_sn
