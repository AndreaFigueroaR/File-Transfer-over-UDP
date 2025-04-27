from lib.client_rdt import ClientRDT

UPLOAD = 'U'
DOWNLOAD = 'D'

READ_BINARY = 'rb'
WRITE_BINARY ='wb'
CHUNK_SIZE = 1024

class Client:
    def __init__(self, srv_host, srv_port, protocol):
        self.srv_addr = (srv_host, srv_port)
        self.prot_type = protocol

    def upload(self, file_path):
        self._start(file_path, UPLOAD)

    def download(self, file_path):
        self._start(file_path, DOWNLOAD)

    def _start(self, file_path, client_type):
        rdt = None
        try:
            rdt = ClientRDT(self.srv_addr)
            rdt.start(self.prot_type, client_type, file_path)
            print("handshake terminó")
            #self._dispatch_client(file_path, client_type, rdt)
        except ValueError as error:
            print(f"Error: {error}")
        except Exception as e:
            print(f"Unknown error: {e}")
        if rdt: rdt.stop()

    def _dispatch_client(self, file_path, client_type, rdt):
        if client_type == UPLOAD:
            self._handle_client_upload(file_path, rdt)
        elif client_type == DOWNLOAD:
            self._handle_client_download(file_path, rdt)

    def _handle_client_upload(self, file_path, rdt):
        with open(file_path, READ_BINARY) as file:
            self._send_file(file, rdt)
        
    def _handle_client_download(self, file_path, rdt):
        with open(file_path, WRITE_BINARY) as file:
            self._recv_file(file, rdt)

    def _recv_file(self, file, rdt):
        while True:
            data = rdt.receive()
            if not data:
                break
            file.write(data)
        
    def _send_file(self, file, rdt):
        while True:
            data = file.read(CHUNK_SIZE)
            if not data:
                break
            rdt.send(data)
