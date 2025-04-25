from lib.parser import parser
import random
import socket
import time

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
TIME_OUT = 0.1
TAM_BUFFER = 1024


def main():
    args = parser.parse_download()
    if args.verbose:
        print("[INFO] Verbose mode ON")
    elif args.quiet:
        print("[INFO] Quiet mode ON")

    print(
        f"[INFO] Downloading file '{args.name}' from {args.host}:{args.port} using protocol {args.protocol}")

    run(args)


def formated_first_pkt(seq, args) -> str:
    return f"{seq}|D|{args.protocol}|{args.name}"


def try_send_hand_shake_msg(sock, packet, serv_addr):
    sock.sendto(packet.encode(), serv_addr)
    try:
        data_handshake, serv_addr = sock.recvfrom(TAM_BUFFER)
    except socket.timeout:
        try_send_hand_shake_msg(sock, packet, serv_addr)
        time.sleep(1)

    serv_seq, ack = data_handshake.decode().split("|", 1)
    return (serv_seq, ack, serv_addr)


def send_first_hand_shake_msg(sock, seq, args):
    print(f"expecting {seq}")
    serv_seq, ack, serv_addr = try_send_hand_shake_msg(
        sock, formated_first_pkt(
            seq, args), (parser.SERVER_IP, parser.SERVER_PORT))
    while int(ack) != seq:  # reenviando cada que se recibe corrupto
        serv_seq, ack = try_send_hand_shake_msg(sock, seq, args, serv_addr)
        print(
            f"[Error]: some error has ocurred: receive ack {int(ack)}, expecting {seq}. Trying to connect the server again")
    print("logramos")
    return serv_seq, serv_addr


def send_second_hand_shake_msg(sock, serv_seq, serv_addr):
    sock.sendto(str(serv_seq).encode(), serv_addr)


def run(args):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIME_OUT)
    seq = random.randint(1, 100)
    serv_seq, serv_addr = send_first_hand_shake_msg(sock, seq, args)
    send_second_hand_shake_msg(sock, serv_seq, serv_addr)


if __name__ == "__main__":
    main()
