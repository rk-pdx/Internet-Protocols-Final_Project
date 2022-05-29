#!/usr/bin/env python

import socket
import sys

host = "localhost"
port = 6697
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
msgText = "hello world"
msgBytes = msgText.encode() #socket.send() doesn't accept raw strings
s.send(msgBytes)
print((s.recv(20)).decode())
s.close()