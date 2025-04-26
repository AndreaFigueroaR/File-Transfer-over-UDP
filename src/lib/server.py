import socket
import threading

from server_rdt import ServerRDT

READ_BINARY = 'rb'
WRITE_BINARY ='wb'   

TAM_BUFFER = 1024
UPLOAD = 'U'
DOWNLOAD = 'D'

HANDSHAKE_SUCCESS = 0

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
        for cli_id in list(self.clients):
            thread = self.clients[cli_id]
            if not thread.is_alive():
                thread.join()
                del self.clients[cli_id]
    
    def _handle_client(self, client_data, client_addr):
        rdt = ServerRDT(client_addr)
        try:
            app_data = rdt.meet_client(client_data, self.prot_type)
            file_path, client_type = app_data.split('|')
            if client_type == UPLOAD:
                self._handle_client_upload(file_path, rdt)
            elif client_type == DOWNLOAD:
                self._handle_client_download(file_path,rdt)
        except ValueError:
            pass
        rdt.stop() # could raise an exception in the client program
        self._clear_client(client_addr)

    def _handle_client_upload(file_path, rdt):
        with open(file_path, READ_BINARY) as file:
            data = file.read()  
            rdt.send(data)
            
    def _handle_client_download(file_path, rdt):
        data = rdt.recieve()
        with open(file_path, WRITE_BINARY) as file:
            file.write(data)
        
    def _clear_client(self, client_addr):
        self.clients[client_addr].join()
        del self.clients[client_addr]
