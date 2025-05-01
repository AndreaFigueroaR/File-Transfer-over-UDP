from lib.parser import parser
from lib.client import Client


def main():
    args = parser.parse_upload()
    is_verbose = True if args.verbose else False
    client = Client(args.host, args.port, args.protocol, is_verbose)
    client.upload(args.src, args.name)


if __name__ == "__main__":
    main()
