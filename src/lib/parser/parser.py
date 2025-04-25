import argparse

# Contantes de descripción
DESC_SERVER = "File Transfer Server."
DESC_DOWNLOAD = "File Transfer Download."
DESC_UPLOAD = "File Transfer Upload."

# Constantes de paths para guardar archivos
STORAGE_SERVER = './storage/server/'
STORAGE_DOWNLOAD = './storage/download/'

# Constantes de IP y port de Server
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9000

SELECTIVE_REPEAT = "sr"
STOP_AND_WAIT = "sw"


def parse_server():
    parser = parser_commons(DESC_SERVER)

    parser.add_argument(
        "-s",
        "--storage",
        default=STORAGE_SERVER,
        help="storage dir path")

    return parser.parse_args()


def parser_commons(description: str):
    parser = argparse.ArgumentParser(description=description)
    # commons parsers:

    # Para usar sólo uno de los dos. No ambos al ismo tiempo
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose",
                           action="store_true",
                           help="increase output verbosity")
    verbosity.add_argument("-q", "--quiet",
                           action="store_true",
                           help="decrease output verbosity")

    # Main arguments
    parser.add_argument("-H", "--host",
                        default=SERVER_IP,
                        help="service IP address")

    parser.add_argument("-p", "--port",
                        type=int,
                        default=SERVER_PORT,
                        help="service port")

# TODO debe ser excluyente el protocolo de transporte a utilizar
    parser.add_argument("-r", "--protocol",
                        choices=[SELECTIVE_REPEAT, STOP_AND_WAIT],
                        default=STOP_AND_WAIT,
                        help="error recovery protocol")

    return parser


def parse_upload():
    parser = parser_commons(DESC_UPLOAD)
    parser = parse_common_for_client(parser)

    # indica al cliente qué archivo local debe subir al servidor.
    parser.add_argument(
        "-s",
        "--src",
        required=True,
        help="source file path"
    )

    return parser.parse_args()


def parse_download():
    parser = parser_commons(DESC_DOWNLOAD)
    parser = parse_common_for_client(parser)

    # indica al cliente donde guardar archivo
    parser.add_argument(
        "-d",
        "--dst",
        default=STORAGE_DOWNLOAD,
        help="destination file path"
    )

    return parser.parse_args()


def parse_common_for_client(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-n", "--name",
        dest="name",
        required=True,
        metavar="FILENAME",
        help="name of the file to request to the server"
    )
    return parser
