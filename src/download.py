from lib.parser import parser
from lib.client.client import Client
import lib.debug as debug

def main():
    args = parser.parse_download()
    is_verbose = True if args.verbose else False
    debug.verbose = is_verbose
    client = Client(args.host, args.port, args.protocol, is_verbose)
    client.download(args.dst, args.name)


if __name__ == "__main__":
    main()
