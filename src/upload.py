from lib.parser import parser
import socket
import os

TIME_OUT = 0.1
MAX_FILE_SIZE = 5 #MB

def main(args):
    args = parser.parse_upload()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(TIME_OUT)

        server_ip, server_port = args.host, args.port

        file_name = args.name #nombre del archivo como se guardará en el servidor
        source_file_path = args.src # path (local) del archivo que se subirá
        try:
            # De este metodo se debería salir del programa (excepción o bien valor de error retornado)
            check_file_characteristics(source_file_path)
        except:
        # handshake independiente al modo de recuperaciónde errores
        # comunicación durante del handshake siempre estilo stop and wait
        cli_channel_add = upload_handshake(sock, server_ip, server_port, file_name, source_file_path)

def upload_handshake(sock, server_ip, server_port, file_name, source_file_path):    
    first_chunk = (int(0).to_bytes(ID_SIZE, byteorder='big')
                    + UPLOAD.to_bytes(CLIENT_METHOD_SIZE, byteorder='big')
                    + file_size.to_bytes(FILE_SIZE, byteorder='big')
                    + name.ljust(CHUNK_SIZE - ID_SIZE - FILE_SIZE - CLIENT_METHOD_SIZE, '\0').encode('utf-8'))
    sock.sendto(first_chunk, (server_ip, server_port))

###################### secondary functions ######################

def display_mode(args):
    if args.verbose:
        print("[INFO] Verbose mode ON")
    elif args.quiet:
        print("[INFO] Quiet mode ON")
    print(
        f"[INFO] Uploading file '{args.src}' as '{args.name}' to {args.host}:{args.port} using protocol {args.protocol}")
    
def check_file_characteristics(source_file_path) -> int:
    # chequeo de que el path existe y obtener el largo del path
    if not os.path.exists(source_file_path):
        # el printeo mediante una entidad que se encargue de logear los errores
        # dicha entidad consideraría el nivel de verbose
        print('ERROR: archivo inexistente')
        #no puedo hacer un exit porque tengo recursos reservados
        return -1

    file_size = os.path.getsize(source_file_path)
    if file_size > (MAX_FILE_SIZE * 1024 * 1024):
        print('ERROR: Upload invalido a causa de violación de tamaño')
        return -1

if __name__ == "__main__":
    main()
