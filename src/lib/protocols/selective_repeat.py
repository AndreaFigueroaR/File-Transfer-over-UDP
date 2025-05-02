from lib.protocols.protocol_arq import *
import time
import socket

TIMEOUT = 1
MAX_WIN_SIZE = 50


class SelectiveRepeat(ProtocolARQ):
    def send(self, data: bytes):
        current_sn = self.remote_sn
        if len(data) == 0:
            self._send_ack(current_sn)
            return

        self._print_if_verbose(f"Data size to send: {len(data)}")

        data_chunks = self._split_data(data)
        ack_buffer = set()
        win_size = self._set_win_size(len(data_chunks))
        timers = {}
        while current_sn < len(data_chunks):
            # Enviar segmentos dentro de la window para los cuales:
            # no estoy esperando ack y no he recibido ack
            win_end = min(current_sn + win_size, len(data_chunks))
            for sn in range(current_sn, win_end):
                if sn in timers or sn in ack_buffer:
                    continue
                self._send_segment(sn, data_chunks[sn])
                timers[sn] = time.time()

            ack = self._recv_ack()
            self._print_if_verbose(f"{IND}ACK expected: {current_sn}")
            self._print_if_verbose(f"{IND}ACK received: {ack}")
            if ack < current_sn:
                self._print_if_verbose(f"{IND}Received duplicated ACK.")
            elif ack > current_sn:
                ack_buffer.add(ack)
                self._print_if_verbose(f"{IND}Received out of order ACK. Buffered.")
            else:
                self._print_if_verbose(f"{IND}Received expected ACK.")
                current_sn = self._update_current_sn(ack, ack_buffer)
                del timers[ack]
            
            # Reenviar segmentos expirados
            for sn in list(timers):
                if timers[sn] + TIMEOUT <= time.time():
                    self._print_if_verbose(f"{IND}Resending expired segment with ACK {sn}.")
                    self._send_segment(sn, data_chunks[sn])
                    timers[sn] = time.time()

    def receive(self, max_data_size) -> bytearray:
        expected_sn = self.remote_sn
        segments_buffer = {}
        data = bytearray()
        bytes_received = 0
        
        last_segment_acked = -1
        while bytes_received < max_data_size:
            try:
                seq_num, payload = self._recv_segment()
                self._print_if_verbose(f"Sequence number expected: {expected_sn}")
                self._print_if_verbose(f"Sequence number received: {seq_num}")

                if seq_num < expected_sn:
                    self._print_if_verbose(f"{IND}Received duplicated sequence number.")
                elif seq_num > expected_sn:
                    segments_buffer[seq_num] = payload
                    self._print_if_verbose(f"{IND}Received out of order sequence number. Buffered.")
                    self._send_ack(seq_num)
                else:
                    self._print_if_verbose(f"Received expected sequence number.")
                    data.extend(payload)
                    bytes_received += len(payload)
                    self._send_ack(seq_num)
                    last_segment_acked = seq_num
                    if len(payload) < DATA_CHUNK_SIZE:
                        return data
                    
                    # Guardar segmentos consecutivos que estaban en el buffer
                    expected_sn = seq_num + 1
                    while expected_sn in segments_buffer:
                        data.extend(segments_buffer.pop(expected_sn))
                        expected_sn += 1
            except socket.timeout:
                print("[ERROR]: Timeout")
                if last_segment_acked >= 0:
                    self._send_ack(last_segment_acked)
        return data

    def _set_win_size(self, num_segments):
        half = num_segments // 2
        return min(MAX_WIN_SIZE, max(1, half))

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
