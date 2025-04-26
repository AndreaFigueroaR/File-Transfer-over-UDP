from lib.parser import parser
from lib.client import Client


def main(args):
    args = parser.parse_download()
    display_mode(args)

    client = Client(args.host, args.port, args.protocol)
    client.download(args.src)


def display_mode(args):
    if args.verbose:
        print("[INFO] Verbose mode ON")
    elif args.quiet:
        print("[INFO] Quiet mode ON")
    print(
        f"[INFO] Downloading file '{args.name}' from {args.host}:{args.port} using protocol {args.protocol}")


if __name__ == "__main__":
    main()
