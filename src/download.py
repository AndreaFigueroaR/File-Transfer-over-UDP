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


def formated_pkt(seq, args) -> str:
    return f"{seq}|D|{args.protocol}|{args.name}"


def try_send_first_hand_shake_msg(sock, packet):
    sock.sendto(packet.encode(), (parser.SERVER_IP, parser.SERVER_PORT))
    try:
        data_handshake, serv_add = sock.recvfrom(TAM_BUFFER)
    except socket.timeout:
        try_send_first_hand_shake_msg(sock, packet)
        time.sleep(1)

    serv_seq, ack = data_handshake.decode().split("|", 1)
    return (serv_seq, ack)


def senf_first_hand_shake_msg(sock, seq, args):
    print(f"expecting {seq}")
    serv_seq, ack = try_send_first_hand_shake_msg(sock, formated_pkt(seq, args))
    #threading.Timer
    while int(ack) != seq:
        serv_seq, ack = try_send_first_hand_shake_msg(sock, seq, args)
        print(f"[Error]: some error has ocurred: receive ack {int(ack)}, expecting {seq}. Trying to connect the server again")
    print("logramos")
    return serv_seq


def run(args):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIME_OUT)
    seq = random.randint(1, 100)
    serv_seq = senf_first_hand_shake_msg(sock, seq, args)
    #sent_second_hand_shake_msg(sock,serv_seq)

    

if __name__ == "__main__":
    main()
