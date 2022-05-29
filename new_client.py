from os import sep
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
OPCODE_CLIENT_ID = 9
OPCODE_ERROR_MESSAGE = -1

# server will send us an address
# we will send this address with any message we send
my_address = "no address"

# declare TCP socket
s = socket.socket()


def listen_for_messages():
    global my_address
    while True:
        message = s.recv(1024).decode()
        print(message)

        # parse opcode
        x = message.split(separator_token)

        # if no opcode (socket connection message)
        if(len(x) == 1):
            print(message)
            continue
        # if we have an opcode
        opcode = int(x[0])
        message = x[1]

        # if the server is sending us our client ID
        if(opcode == OPCODE_CLIENT_ID):
            my_address = message
            # send back our username so server can link it to client ID
            to_send = f"{OPCODE_SET_USERNAME}{separator_token}{my_address}"\
                f"{separator_token}{name}"
            s.send(to_send.encode())
        # if a chat or message is being sent
        elif(opcode == OPCODE_BROADCAST_MESSAGE):
            print(message)
        # if an error
        elif(opcode == OPCODE_ERROR_MESSAGE):
            print(message)

def keepalive(period):
    #payload = f"{OPCODE_KEEP_ALIVE}{separator_token}"\
    #    f"{my_address}{separator_token}'keepalive'"
    while True:
        payload = f"{OPCODE_KEEP_ALIVE}{separator_token}"\
            f"{my_address}{separator_token}'keepalive'"
        s.send(payload.encode())
        time.sleep(period)

def show_uses():
    print("\nWelcome to the chat room app!\n")
    print("\tTo join a room: /join <room name>")
    print("\tTo list rooms: /list")
    print("\tTo create room: /create <room name>")
    print("\tTo leave room: /leave")
    print()

# initialize TCP socket
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")

# require user name before sending messages
name = input("Enter your name: ")

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

show_uses() # tell user how to use the chat room app

while True:
    # input message we want to send to the server
    to_send = input()

    # if a message starts with '/', it's a command
    if len(to_send) > 0 and to_send[0] == '/':

        # if the client wants to leave the room
        if(to_send == '/leave'):
            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            to_send = f"{OPCODE_LEAVE_ROOM}{separator_token}{my_address}"\
                f"{separator_token}{date_now}{separator_token}{name}"

        # if the client wants to join a room
        elif(to_send.startswith('/join')):
            # what comes after /join is the room name
            x = to_send.split()
            if(len(x) == 2):
                to_send = f"{OPCODE_JOIN_ROOM}{separator_token}{my_address}"\
                    f"{separator_token}{x[1]}"
            else:
                print("\t<Error: wrong number of arguments>")
                continue

        # if the user wants to create a room
        elif(to_send.startswith('/create')):
            # what comes after /create is the room name
            x = to_send.split()
            if(len(x) == 2):
                to_send = f"{OPCODE_CREATE_ROOM}{separator_token}{my_address}"\
                    f"{separator_token}{x[1]}"
            else:
                # respond error
                continue

        # if the user wants to list all rooms
        elif(to_send.startswith('/list')):
            to_send = f"{OPCODE_LIST_ROOMS}{separator_token}{my_address}"\
                f"{separator_token}blank"
        else:
            print('\t<Error: invalid command!>')
            continue

        
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
        to_send = f"{OPCODE_SEND_MESSAGE}{separator_token}{my_address}" \
        f"{separator_token}{client_color}[{date_now}] "\
        f"{name}{separator_token}{to_send}{Fore.RESET}"
    # finally, send the message
    s.send(to_send.encode())

# close the socket
s.close()
