import os
import socket
import threading
import time
import lib.debug as debug
from lib.server.server_rdt import ServerRDT

READ_BINARY = "rb"
WRITE_BINARY = "wb"

TAM_BUFFER = 1024
UPLOAD = 'U'
DOWNLOAD = 'D'

FILE_CHUNK_SIZE = 4096


class Server:
    def __init__(self, host, port, protocol, storage):
        self.addr = (host, port)

        self.skt_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt_listener.bind(self.addr)
        print(
            f"[INFO] Server listening in IP: {host}, PORT:{port} "
            f"using protocol {protocol}")

        self.prot_type = protocol
        self.storage = storage

        if debug.verbose:
            print("[INFO] Verbose mode ON")
        else:
            print("[INFO] Quiet mode ON")

        self.clients = {}

    def accept_clients(self):
        try:
            while True:
                self._reap_dead()
                client_data, client_addr = self.skt_listener.recvfrom(
                    TAM_BUFFER)
                if client_addr not in self.clients:
                    debug.log_result(f"[NEW CLIENT]: got request of conection "
                                     f"of host: {client_addr}")
                    client_thread = threading.Thread(
                        target=self._handle_client, args=(
                            client_data, client_addr))
                    client_thread.start()
                    self.clients[client_addr] = client_thread

        except KeyboardInterrupt:
            self.skt_listener.close()
        finally:
            self._clear()

    def _reap_dead(self):
        for client_addr in list(self.clients):
            thread = self.clients[client_addr]
            if not thread.is_alive():
                thread.join()
                del self.clients[client_addr]

    def deserialize_app_data(self, app_data):
        return app_data[0], app_data[1:]

    def _handle_client(self, client_data, client_addr):
        rdt = None
        try:
            rdt = ServerRDT(client_addr)
            app_data = rdt.meet_client(client_data, self.prot_type)
            client_type, srv_file_name = self.deserialize_app_data(app_data)
            self._dispatch_client(rdt, client_type, srv_file_name)
            debug.log_result(f"Connection with client {client_addr} "
                             f"ended orderly")

        except ValueError as error:
            print(f"[ERROR]: {error}")
        except ConnectionError as e:
            print(f"[ERROR]: {e}")
            return
        except Exception as e:
            print(f"Unknown error: {e}")
        if rdt:
            rdt.stop()

    def _dispatch_client(self, rdt, client_type, srv_file_name):
        if client_type == UPLOAD:
            self._handle_client_upload(rdt, self.storage, srv_file_name)
        elif client_type == DOWNLOAD:
            self._handle_client_download(rdt, srv_file_name)

    def _handle_client_upload(self, rdt, storage, srv_file_name):
        os.makedirs(storage, exist_ok=True)
        srv_file_path = os.path.join(storage, srv_file_name)
        with open(srv_file_path, WRITE_BINARY) as file:
            self._recv_file(rdt, file)
        print("[INFO] File received")

    def _handle_client_download(self, rdt, srv_file_name):
        if not os.path.isfile(srv_file_name):
            raise FileNotFoundError(f"File {srv_file_name} does not exist.")
        with open(srv_file_name, READ_BINARY) as file:
            self._send_file(rdt, file)
        print("[INFO] File sended")

    def _recv_file(self, rdt, file):
        start = time.time()
        bytes_received = 0
        while True:
            data = rdt.receive()
            print(f"[FILE] Data chunk bytes received: {len(data)}")
            if not data:
                break
            file.write(data)
            bytes_received += len(data)
        elapsed = time.time() - start
        print(
            f"[FILE] Total bytes received {bytes_received} in {elapsed:.3f} s")

    def _send_file(self, rdt, file):
        start = time.time()
        bytes_sended = 0

        while True:
            data = file.read(FILE_CHUNK_SIZE)
            if not data:
                break
            bytes_sended += len(data)
            rdt.send(data)
        rdt.send(bytes())
        elapsed = time.time() - start
        print(f"[FILE] Total bytes sended {bytes_sended} in {elapsed:.3f} s")

    def _clear(self):
        for client_addr in list(self.clients.keys()):
            self.clients[client_addr].join()
            del self.clients[client_addr]
