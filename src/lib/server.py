import socket
import threading

from server_rdt import ServerRDT

READ_BINARY = 'rb'
WRITE_BINARY ='wb'

TAM_BUFFER = 1024
UPLOAD = 'U'
DOWNLOAD = 'D'

HANDSHAKE_SUCCESS = 0
CHUNK_SIZE = 1024

class Server: 
    def __init__(self, host, port, protocol):
        self.skt_acceptor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skt_acceptor.bind(self.addr)
        self.addr = (host, port)
        self.prot_type = protocol
        self.clients = {}

    def accept_clients(self):
        print("[INFO] Server is ready to receive...")
        while True:
            client_data, client_addr = self.skt_acceptor.recvfrom(TAM_BUFFER)
            print(f"[INFO] Client {client_addr}: {client_data.decode()} started contact with the server")
            client_thread = threading.Thread(target=self._handle_client, args=(client_data, client_addr))
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
            file_path, client_type = app_data.split('|')
            self._dispatch_client(file_path, client_type, rdt)
        except ValueError as error:
            print(f"Error meeting client: {error}")
        except Exception as e:
            print(f"Unknown error: {e}")
            
        if rdt: rdt.stop()
        self._clear_client(client_addr)
        
    def _dispatch_client(self, file_path, client_type, rdt):
        if client_type == UPLOAD:
            self._handle_client_upload(file_path, rdt)
        elif client_type == DOWNLOAD:
            self._handle_client_download(file_path, rdt)

    def _handle_client_upload(self, file_path, rdt):
        with open(file_path, WRITE_BINARY) as file:
            self._recv_file(file, rdt)

    def _handle_client_download(self, file_path, rdt):
        with open(file_path, READ_BINARY) as file:
            self._send_file(file, rdt)

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
        
    def _clear_client(self, client_addr):
        self.clients[client_addr].join()
        del self.clients[client_addr]
