import os
import sys
import socket
import threading
from lib.parser import parser

TAM_BUFFER = 1024
SEQ = 42


def handle_client(data, addr):
    print(f"[RECV] From {addr}: {data.decode()}")

    # Simular respuesta tipo SEQ|ACK [SEQ,ACK]
    response = f"{SEQ}|{data.decode().split('|')[0]}".encode()
    print("ENVIO A CLIENTE:")
    print(response.decode())
    sock_per_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock_per_client.sendto(response, addr)
    print(f"[SEND] Sent SEQ|ACK to {addr}")


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

    print(f"[INFO] Server listening in IP: {args.host}, PORT:{args.port} using protocol {args.protocol}")
    run_acceptor(args)


if __name__ == "__main__":
    main()


