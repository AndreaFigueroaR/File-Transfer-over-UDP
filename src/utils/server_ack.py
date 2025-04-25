# servidor.py
import socket
import threading
import time

from queue import Queue

HOST = "0.0.0.0"
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

client_queues = {}      # (ip, port) -> Queue
client_threads = {}     # (ip, port) -> Thread
client_expected_seq = {}  # (ip, port) -> expected sequence
lock = threading.Lock()


def handle_client(addr, q):
    print(f"durmiendo 20s")
    time.sleep(20)
    print("desperté")
    while True:
        data = q.get()  # probabalemente se cambie
        if data is None:
            break  # Por si querés cerrar después

        try:
            message = data.decode()
            seq_str, content = message.split("|", 1)
            seq = int(seq_str)
        except Exception as e:
            print(f"[{addr}] Paquete inválido: {e}")
            continue

        with lock:
            expected = client_expected_seq.get(addr, 0)

        if seq == expected:
            print(f"[{addr}] Recibido (seq={seq}): {content}")
            # Enviar ACK
            sock.sendto(str(seq).encode(), addr)
            with lock:
                client_expected_seq[addr] = 1 - expected
        else:
            print(
                f"[{addr}] Duplicado o fuera de orden. Reenviando ACK {1 - expected}")
            sock.sendto(str(1 - expected).encode(), addr)


def dispatcher():
    print(f"[+] Servidor escuchando en {HOST}:{PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        print(addr)
        with lock:
            if addr not in client_queues:
                print(f"[+] Servidor aceptó al client con addr {addr}")
                q = Queue()
                client_queues[addr] = q
                # esto creo que debería ser random y se intercanbia en el 3
                # manos sahcking
                client_expected_seq[addr] = 0
                t = threading.Thread(
                    target=handle_client, args=(
                        addr, q), daemon=True)
                client_threads[addr] = t
                t.start()
        client_queues[addr].put(data)


if __name__ == "__main__":
    dispatcher()
