#!/usr/bin/env python

import select
import socket
import sys

host = ""
port = 6697
queue = 5 #temp value
size = 1024 #temp value
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(queue)
input = [s, sys.stdin]
running = 1
while(running):
    inputready, outputready, exceptready = select.select(input, [], [])
    
    for x in inputready:
        if x == s:
            client, addr = s.accept()
            input.append(client)

        elif x == sys.stdin:
            temp = sys.stdin.readline()
            running = 0

        else:
            data = x.recv(size)
            if data:
                x.send(data)
            else:
                x.close()
                input.remove(x)

s.close()