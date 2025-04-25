import os
import sys
from lib.parser import parser


def main():
    args = parser.parse_server()

    if args.verbose:
        print("[INFO] Verbose mode ON")
    elif args.quiet:
        print("[INFO] Quiet mode ON")

    print(
        f"[INFO] Server listeneing in IP: {args.host}, PORT:{args.port} using protocol {args.protocol}")


if __name__ == "__main__":
    main()
