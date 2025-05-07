import socket
import time


def estimate_timeout(sock, remote_addr, is_server=False, attempts=5):
    tiempos = []

    for _ in range(attempts):
        try:
            if is_server:
                sock.settimeout(2)
                data, addr = sock.recvfrom(1024)
                if data != b"PING":
                    continue
                start = time.time()
                sock.sendto(b"PONG", addr)
                end = time.time()
            else:
                sock.sendto(b"PING", remote_addr)
                start = time.time()
                sock.settimeout(2)
                data, _ = sock.recvfrom(1024)
                end = time.time()
                if data != b"PONG":
                    continue

            tiempos.append(end - start)

        except socket.timeout:
            continue

    if tiempos:
        rtt_promedio = sum(tiempos) / len(tiempos)
        return max(0.001, rtt_promedio * 2)
    else:
        # En compus rapidas es un buen default. Pero hay que probar si con este
        # timeout cumple lo de menos de dos minutos en cualquiera.
        return 0.5
