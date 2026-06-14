"""Generate QR code for the certificate page and start a local server."""

import argparse
import socket
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    import qrcode
except ImportError:
    print("Installing qrcode package...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "qrcode[pil]", "-q"])
    import qrcode


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def generate_qr(url: str, output: Path) -> None:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output)
    print(f"QR code saved: {output}")
    print(f"Scan URL: {url}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve certificate page and generate QR code")
    parser.add_argument("--port", type=int, default=8080, help="HTTP port (default: 8080)")
    parser.add_argument("--url", type=str, default="", help="Custom URL for QR code")
    parser.add_argument("--no-serve", action="store_true", help="Only generate QR, do not start server")
    args = parser.parse_args()

    root = Path(__file__).parent.resolve()
    qr_path = root / "qr-code.png"

    ip = get_local_ip()
    url = args.url or f"http://{ip}:{args.port}/index.html"

    generate_qr(url, qr_path)

    if args.no_serve:
        return

    print(f"\nStarting server at http://{ip}:{args.port}/")
    print("Press Ctrl+C to stop.\n")

    import os
    os.chdir(root)
    server = ThreadingHTTPServer(("0.0.0.0", args.port), SimpleHTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
