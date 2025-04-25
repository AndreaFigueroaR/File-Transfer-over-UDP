from lib.parser import parser


def main():
    args = parser.parse_download()

    if args.verbose:
        print("[INFO] Verbose mode ON")
    elif args.quiet:
        print("[INFO] Quiet mode ON")

    print(
        f"[INFO] Downloading file '{args.name}' from {args.host}:{args.port} using protocol {args.protocol}")


if __name__ == "__main__":
    main()
