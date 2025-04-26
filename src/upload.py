from lib.parser import parser
from lib.client import Client

# MAX_FILE_SIZE = 5 #MB

# class FileCheckError(Exception):
#     """Error en validación de archivo previo al envío."""
#     pass

UPLOAD = 'U'

def main(args):
    args = parser.parse_upload()
    display_mode(args)
    
    client = Client(UPLOAD, args.protocol)
    client.upload(args.src)

# metodo del client
# def check_file_exists_or_fail(source_file_path):
#     if not os.path.exists(source_file_path):
#         raise FileCheckError(f"Nonexistent file {source_file_path}")

#     file_size = os.path.getsize(source_file_path)
#     if file_size > (MAX_FILE_SIZE * 1024 * 1024):
#         raise FileCheckError("Upload invalido a causa de violación de tamaño")

def display_mode(args):
    if args.verbose:
        print("[INFO] Verbose mode ON")
    elif args.quiet:
        print("[INFO] Quiet mode ON")
    print(
        f"[INFO] Uploading file '{args.src}' as '{args.name}' to {args.host}:{args.port} using protocol {args.protocol}")

if __name__ == "__main__":
    main()
