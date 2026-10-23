"""`hwp2md serve`: run the local web preview server."""

from __future__ import annotations

import socket
import sys
import threading
import webbrowser

import uvicorn

from .app import create_app

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8765


def _port_available(host: str, port: int) -> bool:
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError:
        return False
    family, socktype, proto, _canon, addr = infos[0]
    with socket.socket(family, socktype, proto) as sock:
        try:
            sock.bind(addr)
        except OSError:
            return False
    return True


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, *, open_browser: bool = True) -> int:
    if not _port_available(host, port):
        print(f"hwp2md: error: port {port} already in use", file=sys.stderr)
        return 1
    url = f"http://{host}:{port}/"
    print(f"hwp2md serve: {url} (Ctrl+C 로 종료)", flush=True)
    if open_browser:
        timer = threading.Timer(1.0, webbrowser.open, [url])
        timer.daemon = True
        timer.start()
    try:
        uvicorn.run(create_app(), host=host, port=port, log_level="warning")
    except KeyboardInterrupt:
        return 0
    return 0
