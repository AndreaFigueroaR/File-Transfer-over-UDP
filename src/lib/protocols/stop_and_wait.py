from lib.protocols.selective_repeat import SelectiveRepeat


class StopAndWait():
    def __init__(self, socket, remote_address):
        self.prot_sr = SelectiveRepeat(socket, remote_address)
        self.prot_sr.set_win_size(1)

    def send(self, data):
        self.prot_sr.send(data)

    def receive(self):
        return self.prot_sr.receive()
