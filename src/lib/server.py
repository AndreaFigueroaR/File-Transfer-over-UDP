import os
import socket
import threading

from lib.server_rdt import ServerRDT

READ_BINARY = "rb"
WRITE_BINARY = "wb"

TAM_BUFFER = 1024
UPLOAD = 'U'
DOWNLOAD = 'D'

HANDSHAKE_SUCCESS = 0
CHUNK_SIZE = 1024


class Server:
    def __init__(self, host, port, protocol, storage):
        self.addr = (host, port)
        self.skt_acceptor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt_acceptor.bind(self.addr)
        self.prot_type = protocol
        self.storage = storage
        self.clients = {}


    def accept_clients(self):
        # TODO: catchear excepcion KeyboardInterrupt.
        while True:
            client_data, client_addr = self.skt_acceptor.recvfrom(TAM_BUFFER)
            client_thread = threading.Thread(
                target=self._handle_client, args=(
                    client_data, client_addr))
            client_thread.start()
            self.clients[client_addr] = client_thread
            self._reap_dead()


    def _reap_dead(self):
        for client_addr in list(self.clients):
            thread = self.clients[client_addr]
            if not thread.is_alive():
                thread.join()
                del self.clients[client_addr]


    def _handle_client(self, client_data, client_addr):
        rdt = None
        try:
            rdt = ServerRDT(client_addr)
            app_data = rdt.meet_client(client_data, self.prot_type)
            client_type, srv_file_name = app_data.split('|')
            self._dispatch_client(rdt, client_type, srv_file_name)
        except ValueError as error:
            print(f"Error meeting client: {error}")
        except ConnectionError as e:
            print(f"Error at handshake: {e}")
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


    def _handle_client_download(self, rdt, srv_file_name):
        # TODO: chequear si el archivo existe. Sino lanzar excepcion.
        with open(srv_file_name, READ_BINARY) as file:
            self._send_file(rdt, file)

    def _recv_file(self, rdt, file):
        while True:
            data = rdt.receive(CHUNK_SIZE)
            file.write(data)
            if len(data) < CHUNK_SIZE:
                break

    def _send_file(self, rdt, file):
        while True:
            data = file.read(CHUNK_SIZE)
            rdt.send(data)
            if not data:
                break

    def _clear_client(self, client_addr):
        self.clients[client_addr].join()
        del self.clients[client_addr]
