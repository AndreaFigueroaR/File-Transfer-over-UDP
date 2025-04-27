import socket
import os


SERVER_HOST = "0.0.0.0"
SERVER_PORT = 12345
FILE_TO_SEND = "aceituna.png"  # Asegúrate de que esté en la misma carpeta
CHUNK_SIZE = 1024
TIMEOUT = 2

CANT_ATTEMPS_FOR_SENDING_MSG = 10
TAM_BUFFER = 1024

def try_send_handshake_msg(packet,client_addr,skt) :
    for _ in range(CANT_ATTEMPS_FOR_SENDING_MSG):
        try:
            skt.sendto(packet, client_addr)
            ack,client_addr = skt.recvfrom(TAM_BUFFER)
        except socket.timeout:
            continue
        return ack.decode()
    print(f"[Error]: maximum number of attempts to send message was reached")


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_HOST, SERVER_PORT))
print(f"Servidor listo para enviar '{FILE_TO_SEND}'...")

# Handshake inicial
_, client_addr = sock.recvfrom(1)
print(f"Cliente conectado: {client_addr}")

# Enviar archivo
seq_num = 0
with open(FILE_TO_SEND, "rb") as file:
    while True:
        
        chunk = file.read(CHUNK_SIZE)
        if not chunk:
            try_send_handshake_msg(packet,client_addr,sock)
            # sock.sendto(seq_num, client_addr)

            # No hacer break. #Despedirme amablemente
            # if despedirme amablemente:
                #break
            break  # Fin del archivo
        

        while True:  # Loop hasta recibir ACK correcto
            packet = seq_num.to_bytes(1, byteorder="big") + chunk
            # 0| dgwygfhjeofm
            sock.sendto(packet, client_addr)
            print(f"Enviado chunk #{seq_num} ({len(chunk)} bytes)")

            try:
                sock.settimeout(TIMEOUT)
                ack, _ = sock.recvfrom(1)
                if int.from_bytes(ack, byteorder="big") == seq_num:
                    seq_num = 1 - seq_num
                    break
            except socket.timeout:
                print(f"Timeout. Reenviando chunk #{seq_num}")

# Señal de fin
sock.sendto(b"\xFF", client_addr)
print("Archivo enviado completamente.")
sock.close()



# def send_despedida_msg( skt_peer,packet):
#     _ = try_send_handshake_msg(skt_peer, packet)
    

