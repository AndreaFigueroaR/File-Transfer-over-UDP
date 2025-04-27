from lib.parser import parser
from lib.client import Client


def main():
    args = parser.parse_upload()
    display_mode(args)

    client = Client(args.host, args.port, args.protocol)
    client.upload(args.src, args.name)


def display_mode(args):
    if args.verbose:
        print("[INFO] Verbose mode ON")
    elif args.quiet:
        print("[INFO] Quiet mode ON")
    print(
        f"[INFO] Uploading file '{args.src}' as '{args.name}' to {args.host}:{args.port} using protocol {args.protocol}")


if __name__ == "__main__":
    main()
