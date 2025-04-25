import os
import sys
import socket
import threading
from lib.parser import parser
import random

TAM_BUFFER = 1024
TIME_OUT = 0.1


def handle_client(data, addr):
    print(f"[RECV] From {addr}: {data.decode()}")

    # Simular respuesta tipo SEQ|ACK [SEQ,ACK]
    seq = random.randint(1, 100)
    response = f"{seq}|{data.decode().split('|')[0]}".encode()
    print("ENVIO A CLIENTE:")
    print(response.decode())
    sock_per_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_per_client.sendto(response, addr)
    socket.timeout(TIME_OUT)
    print(f"[SEND] Sent SEQ|ACK to {addr}")

    # me re envian el num seq
    # manjear segundo handshake
    try:
        client_data, client_addr = sock_per_client.recvfrom(TAM_BUFFER)
        print(
            f"Segundo mensaje del cliente {client_addr}: {client_data.decode()}")
        client_seq = client_data.decode()
        if int(client_seq) == seq:
            print("Segundo_seq es correcto.")
        else:
            print("Segundo_seq es inccorrecto")

    except socket.timeout:
        print("No se recibió ningún mensaje.")


def run_acceptor(args):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((args.host, args.port))
    print("[INFO] Server is ready to receive...")
    # clients = []
    while True:
        data, addr = server_socket.recvfrom(TAM_BUFFER)
        thread = threading.Thread(target=handle_client, args=(data, addr))
        thread.start()
        # clients.append() #<- hacer join


def main():
    args = parser.parse_server()

    if args.verbose:
        print("[INFO] Verbose mode ON")
    elif args.quiet:
        print("[INFO] Quiet mode ON")

    print(
        f"[INFO] Server listening in IP: {args.host}, PORT:{args.port} using protocol {args.protocol}")
    run_acceptor(args)


if __name__ == "__main__":
    main()
