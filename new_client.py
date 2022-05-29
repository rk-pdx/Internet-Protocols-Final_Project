import socket
import random
import time
from threading import Thread
from datetime import datetime
from colorama import Fore, init, Back


init()


colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX, 
    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, 
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, 
    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
]


client_color = random.choice(colors)


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5002 # server's port
separator_token = "<SEP>" # we will use this to separate the client name & message
KEEP_ALIVE_INTERVAL = 5 #seconds
OPCODE_KEEP_ALIVE = 0
OPCODE_SET_USERNAME = 1
OPCODE_CREATE_ROOM = 2
OPCODE_LIST_ROOMS = 3
OPCODE_JOIN_ROOM = 4
OPCODE_LEAVE_ROOM = 5
OPCODE_SEND_MESSAGE = 6
OPCODE_LIST_ROOMS_RESP = 7
OPCODE_BROADCAST_MESSAGE = 8

# declare TCP socket
s = socket.socket()

def listen_for_messages():
    while True:
        message = s.recv(1024).decode()
        print("\n" + message)

def keepalive(period):
    payload = f"{OPCODE_KEEP_ALIVE}{separator_token}'keepalive'"
    while True:
        s.send(payload.encode())
        time.sleep(period)

# initialize TCP socket
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")

# require user name before sending messages
name = input("Enter your name: ")
to_send = f"{OPCODE_SET_USERNAME}{separator_token}{name}"
s.send(to_send.encode())


# make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages)
# make the thread daemon so it ends whenever the main thread ends
t.daemon = True
# start the thread
t.start()

# make a thread that sends keepalive messages to the server
tk = Thread(target=keepalive, args=(KEEP_ALIVE_INTERVAL,))
# make the thread daemon so it ends whenever the main thread ends
tk.daemon = True
# start the thread
tk.start()

while True:
    # input message we want to send to the server
    to_send =  input()
    # a way to exit the program
    if to_send.lower() == 'q':
        break
    elif to_send.lower().startswith('nick'):
        x = to_send.split(' ')
        if len(x) == 2:
            name = x[1]
            to_send = f"{OPCODE_SET_USERNAME}{separator_token}{name}"
    elif to_send.lower() == 'list':
        to_send = f"{OPCODE_LIST_ROOMS}{separator_token}list"
    else:
        # add the datetime, name & the color of the sender
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        to_send = f"{OPCODE_SEND_MESSAGE}{separator_token}{client_color}[{date_now}] \
        {name}{separator_token}{to_send}{Fore.RESET}"
    # finally, send the message
    s.send(to_send.encode())

# close the socket
s.close()
