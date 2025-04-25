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
    print(f"[SEND] Sent SEQ|ACK to {addr}")

    # me re envian el num seq
    # manjear segundo handshake
    try:
        socket.timeout(TIME_OUT)
        second_addr, second_data = socket.recvfrom(TAM_BUFFER)
        print(
            f"Segundo mensaje del cliente {second_addr}: {second_data.decode()}")
        second_seq = second_data.decode().strip()
        if second_seq == seq:
            print("Segundo_seq es correcto.")
        else:
            print("Segundo_seq es inccorrecto")

    except socket.timeout:
        print("No se recibió ningún mensaje.")


def run_acceptor(args):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((args.host, args.port))
    print("[INFO] Server is ready to receive...")

    while True:
        data, addr = server_socket.recvfrom(TAM_BUFFER)
        thread = threading.Thread(target=handle_client, args=(data, addr))
        thread.start()


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
