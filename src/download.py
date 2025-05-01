from lib.parser import parser
from lib.client import Client


def main():
    args = parser.parse_download()
    is_verbose = True if args.verbose else False
    client = Client(args.host, args.port, args.protocol, is_verbose)
    client.download(args.dst, args.name)


if __name__ == "__main__":
    main()
