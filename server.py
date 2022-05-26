#!/usr/bin/env python

import select
import socket
import sys

host = ""
port = 6697
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)
while(1):
    conn, addr = s.accept()
    data = conn.recv(20)
    conn.send(data)
    conn.close()