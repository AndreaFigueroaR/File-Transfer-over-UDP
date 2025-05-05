import os
import time

from lib.client.client_rdt import ClientRDT

UPLOAD = 'U'
DOWNLOAD = 'D'

READ_BINARY = "rb"
WRITE_BINARY = "wb"
CHUNK_SIZE = 1024


class Client:
    def __init__(self, srv_host, srv_port, protocol, is_verbose):
        self.srv_addr = (srv_host, srv_port)
        self.prot_type = protocol
        self.is_verbose = is_verbose
        if is_verbose:
            print("[INFO] Verbose mode ON")
        else: 
            print("[INFO] Quiet mode ON")

    def upload(self, client_src, srv_file_name):
        print(f"[INFO] Uploading file '{client_src}' as '{srv_file_name}' to {self.srv_addr[0]}:{self.srv_addr[1]} using protocol {self.prot_type}")
        self._start(client_src, srv_file_name, UPLOAD)

    def download(self, client_dst, srv_file_name):
        print(f"[INFO] Downloading file '{srv_file_name}' from {self.srv_addr[0]}:{self.srv_addr[1]} using protocol {self.prot_type}")
        self._start(client_dst, srv_file_name, DOWNLOAD)

    def _start(self, client_file_path, srv_file_name, client_type):
        rdt = None
        try:
            rdt = ClientRDT(self.srv_addr)
            rdt.start(self.prot_type, client_type, srv_file_name, self.is_verbose)
            self._dispatch_client(rdt, client_type, client_file_path, srv_file_name)
        except ValueError as error:
            print(f"[ERROR]: {error}")
        except ConnectionError as e:
            print(f"[ERROR]: {e}")
            return
        except Exception as e:
            print(f"Unknown error: {e}")
        if rdt:
            rdt.stop()

    def _dispatch_client(self, rdt, client_type, client_file_path, srv_file_name):
        if client_type == UPLOAD:
            self._handle_client_upload(rdt, client_file_path)
        elif client_type == DOWNLOAD:
            storage = os.path.dirname(client_file_path)
            client_file_name = self._get_client_file_name(client_file_path, srv_file_name)
            self._handle_client_download(rdt, storage, client_file_name)

    def _handle_client_upload(self, rdt, client_src_path):
        if not os.path.isfile(client_src_path):
            raise FileNotFoundError(f"File {client_src_path} does not exist.")
        with open(client_src_path, READ_BINARY) as file:
            self._send_file(rdt, file)
        print("[INFO] File sended")

    def _handle_client_download(self, rdt, storage, client_file_name):
        os.makedirs(storage, exist_ok=True)
        client_dst_path = os.path.join(storage, client_file_name)
        with open(client_dst_path, WRITE_BINARY) as file:
            self._recv_file(rdt, file)
        print("[INFO] File received")

    def _get_client_file_name(self, client_file_path, srv_file_name):
        client_file_name = os.path.basename(client_file_path)
        if not client_file_name:
            client_file_name = srv_file_name
        return client_file_name

    def _send_file(self, rdt, file):
        while True:
            data = file.read(CHUNK_SIZE)
            rdt.send(data)
            if not data:
                break

    def _recv_file(self, rdt, file):
        start = time.time()
        bytes_received = 0
        while True:
            data = rdt.receive()
            if not data:
                break
            file.write(data)
            bytes_received += len(data)
            print(f"Data chunk bytes received: {bytes_received}")
        elapsed = time.time() - start
        print(f"Total bytes received {bytes_received} in {elapsed:.3f} s")
