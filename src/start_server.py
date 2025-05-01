from lib.parser import parser
from lib.server import Server


def main():
    args = parser.parse_server()
    is_verbose = True if args.verbose else False
    server = Server(args.host, args.port, args.protocol, args.storage, is_verbose)
    server.accept_clients()


if __name__ == "__main__":
    main()
