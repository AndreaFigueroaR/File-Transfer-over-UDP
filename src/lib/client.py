from lib.client_rdt import ClientRDT

UPLOAD = 'U'
DOWNLOAD = 'D'

READ_BINARY = "rb"
WRITE_BINARY = "wb"
CHUNK_SIZE = 1024


class Client:
    def __init__(self, srv_host, srv_port, protocol):
        self.srv_addr = (srv_host, srv_port)
        self.prot_type = protocol

    def upload(self, src, file_name):
        self._start(src, file_name, UPLOAD)

    def download(self, dst, file_name):
        self._start(dst, file_name, DOWNLOAD)

    def _start(self, file_path, file_name, client_type):
        rdt = None
        try:
            rdt = ClientRDT(self.srv_addr)
            rdt.start(self.prot_type, client_type, file_name)
            self._dispatch_client(rdt, client_type, file_path)
        except ValueError as error:
            print(f"Error: {error}")
        except ConnectionError as e:
            print(f"Error at handshake: {e}")
            return
        except Exception as e:
            print(f"Unknown error: {e}")
        if rdt:
            rdt.stop()

    def _dispatch_client(self, rdt, client_type, file_path):
        if client_type == UPLOAD:
            self._handle_client_upload(rdt, file_path)
        elif client_type == DOWNLOAD:
            self._handle_client_download(rdt, file_path)

    def _handle_client_upload(self, rdt, file_path):
        with open(file_path, READ_BINARY) as file:
            self._send_file(rdt, file)

    def _handle_client_download(self, rdt, file_path):
        with open(file_path, WRITE_BINARY) as file:
            self._recv_file(rdt, file)

    def _send_file(self, rdt, file):
        while True:
            data = file.read(CHUNK_SIZE)
            rdt.send(data)
            if not data:
                break

    def _recv_file(self, rdt, file):
        while True:
            data = rdt.receive(CHUNK_SIZE)
            file.write(data)
            if len(data) < CHUNK_SIZE:
                break