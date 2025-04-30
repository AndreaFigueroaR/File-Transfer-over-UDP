from lib.parser import parser
from lib.server import Server


def main():
    args = parser.parse_server()
    display_mode(args)

    server = Server(args.host, args.port, args.protocol, args.storage)
    server.accept_clients()


def display_mode(args):
    if args.verbose:
        print("[INFO] Verbose mode ON")
    elif args.quiet:
        print("[INFO] Quiet mode ON")
    print(
        f"[INFO] Server listening in IP: {args.host}, PORT:{args.port} using protocol {args.protocol}")


if __name__ == "__main__":
    main()
