# cliente.py
import socket
import time

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

TIME_OUT = 0.1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(TIME_OUT)  # 1 segundo de espera por ACK

seq = 0
mensajes = [
    "Hola servidor",
    "¿Cómo estás?",
    "Mensaje 3",
    "Fin del test"
]

for msg in mensajes:
    enviado = False
    while not enviado:
        paquete = f"{seq}|{msg}"
        sock.sendto(paquete.encode(), (SERVER_IP, SERVER_PORT))
        print(f"[CLIENTE] Enviado (seq={seq}): {msg}")

        try:
            data, _ = sock.recvfrom(1024)
            ack = int(data.decode())
            if ack == seq:
                print(f"[CLIENTE] ACK recibido: {ack}")
                seq = 1 - seq
                enviado = True
            else:
                print(f"[CLIENTE] ACK incorrecto: {ack}, reintentando...")
        except socket.timeout:
            print("[CLIENTE] Timeout, reenviando...")

print("[CLIENTE] Mensajes enviados correctamente.")
sock.close()
