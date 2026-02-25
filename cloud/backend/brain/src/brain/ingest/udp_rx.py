import socket
import threading
from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class LatestPacket:
    raw: bytes = b""
    addr: tuple[str, int] | None = None

class UdpReceiver:
    def __init__(self, host: str, port: int, bufsize: int = 2048,
                 on_packet: Optional[Callable[[bytes, tuple[str,int]], None]] = None):
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.on_packet = on_packet

        self.latest = LatestPacket()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        sock.settimeout(0.5)

        while not self._stop.is_set():
            try:
                data, addr = sock.recvfrom(self.bufsize)
                self.latest = LatestPacket(raw=data, addr=addr)
                if self.on_packet:
                    self.on_packet(data, addr)
            except TimeoutError:
                continue
            except OSError:
                break
