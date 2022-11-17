from __future__ import annotations

from time import time
from typing import List
import socket
import ssl
from custom_logger import Color as c

results = []
class SocketConn:
    def __init__(self, dataload: str, bytes_amt: int) -> None:
        self.sock = None
        self.dataload = dataload
        self.bytes_amt = bytes_amt

    def conn(self) -> None:
        socke = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socke.connect(('api.minecraftservices.com', 443))
        wrap = ssl.create_default_context().wrap_socket(socke, server_hostname="api.minecraftservices.com")
        self.sock = wrap

    def sock_send(self) -> None:
    	self.sock.send(bytes(f"{self.dataload}\r\n\r\n", "utf-8"))

    def sock_recv(self) -> None:
        results.append((self.sock.recv(self.bytes_amt).decode("utf-8")[9:12]))

    def sock_close(self) -> None:
    	self.sock.close()
     
def ping(num_ping: int) -> float:
    """auto delay"""
    delays: List[float] = []
    test_payload = ("PUT /minecraft/profile/name/TEST HTTP/1.1\r\nHost: api.minecraftservices.com\r\nAuthorization: Bearer " + "TEST_TOKEN\r\n\r\n", "utf-8")
    socket_connection = SocketConn(test_payload, 1024)
    socket_connection.conn()
    for _ in range(num_ping):
        start = time()
        socket_connection.sock_send()
        socket_connection.sock_recv()
        end = time()
        delays.append(end - start)
    socket_connection.sock_close()
    auto_offset = int((sum(delays) / len(delays) * 4000 / 2) + 5)
    return auto_offset