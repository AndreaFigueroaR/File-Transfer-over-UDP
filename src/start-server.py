from lib.parser import parser
from lib.server.server import Server
import lib.debug as debug


def main():
    args = parser.parse_server()
    is_verbose = True if args.verbose else False
    debug.verbose = is_verbose
    server = Server(args.host, args.port, args.protocol, args.storage)
    server.accept_clients()


if __name__ == "__main__":
    main()
