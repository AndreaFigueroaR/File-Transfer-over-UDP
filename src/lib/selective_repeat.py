from protocol_arq import ProtocolARQ


class SelectiveRepeat(ProtocolARQ):

    def __init__(self):
        self.win_size = 4  # calcular
        pass

    def _recv_segment(self):
        # implementar
        pass

    def _send_segment(self):
        # implementar
        pass

    def _formated_first_pkt_client(name, type_client, seq) -> str:
        return f"{seq}|{type_client}|sr|{name}"

    def stop(self):
        self.socket.close()
