from lib.parser import parser
from lib.server import Server
from lib.client import Client
 
DOWNLOAD = 'D'

def main():
    args = parser.parse_download()
    display_mode(args)

    client = Client(DOWNLOAD, args.protocol)
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
