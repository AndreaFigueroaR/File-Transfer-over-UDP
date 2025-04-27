import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12345
FILE_TO_SAVE = "foto_recibida.png"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 54321))  # Puerto aleatorio para el cliente

# Handshake
sock.sendto(b"\x00", (SERVER_HOST, SERVER_PORT))
#faltaría setear un timeout!

# Recibir archivo
seq_num = 0
with open(FILE_TO_SAVE, "wb") as file:
    
    while True:
        packet, _ = sock.recvfrom(1 + 1024)  # +1 para el byte de secuencia
        # 00000001 | <payload>
        # 00000000 | <payload>
        # 11111111 ->  lo enviaba a propósito el sender en lugar de un numero de secuencia
        # OJO: como ya no se envia... no es seguro que el receiver reconozca como terminar
        if packet[0] == 0xFF:#-> pregunta si el primer byte es puros unos (255 en decimal)
            break

        current_seq = packet[0]
        if current_seq == seq_num:
            file.write(packet[1:])  # Escribe los datos
            print(f"Recibido chunk #{seq_num} ({len(packet)-1} bytes)")
            sock.sendto(seq_num.to_bytes(1, byteorder="big"), (SERVER_HOST, SERVER_PORT))
            seq_num = 1 - seq_num
        else:
            print(f"Chunk duplicado #{current_seq}. Reenviando ACK #{1 - seq_num}")
            sock.sendto((1 - seq_num).to_bytes(1, byteorder="big"), (SERVER_HOST, SERVER_PORT))

print(f"Archivo guardado como '{FILE_TO_SAVE}'")
sock.close()