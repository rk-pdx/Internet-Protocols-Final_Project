import socket
from threading import Thread

# server's IP address
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5002 # port we want to use
separator_token = "<SEP>" # we will use this to separate the client name & message
OPCODE_KEEP_ALIVE = 0
OPCODE_SET_USERNAME = 1
OPCODE_CREATE_ROOM = 2
OPCODE_LIST_ROOMS = 3
OPCODE_JOIN_ROOM = 4
OPCODE_LEAVE_ROOM = 5
OPCODE_SEND_MESSAGE = 6
OPCODE_LIST_ROOMS_RESP = 7
OPCODE_BROADCAST_MESSAGE = 8
OPCODE_ILLEGAL_OPCODE = -99

# initialize list/set of all connected client's sockets
client_sockets = set()
# create a TCP socket
s = socket.socket()
# make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))
# listen for upcoming connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def listen_for_client(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    while True:
        try:
            # keep listening for a message from `cs` socket
            data = cs.recv(1024).decode()
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)
        else:
            #if we received a message, parse opcode
            x = data.split(separator_token, 1)
            try:
                opcode = int(x[0])
            except ValueError:
                opcode = OPCODE_ILLEGAL_OPCODE
            if len(x) > 1:
                msg = x[1]

            if (opcode == OPCODE_KEEP_ALIVE):
                pass
            elif opcode == OPCODE_SET_USERNAME:
                pass
            elif opcode == OPCODE_CREATE_ROOM:
                pass
            elif opcode == OPCODE_LIST_ROOMS:
                pass
            elif opcode == OPCODE_JOIN_ROOM:
                pass
            elif opcode == OPCODE_LEAVE_ROOM:
                # split to retrieve other fields
                x = data.split(separator_token)
                # if wrong number of args
                if(len(x) != 3):
                    # return error
                    continue
                #otherwise we will handle the leave room
                #
                #notify chat room about the user leaving the room
                for client_socket in client_sockets:
                    client_socket.send((f"{x[1]}: <{x[2]} has left the chat room>").encode())

            elif opcode == OPCODE_SEND_MESSAGE: # send message
                # replace the <SEP> 
                # token with ": " for nice printing
                msg = msg.replace(separator_token, ": ")
                # iterate over all connected sockets
                for client_socket in client_sockets:
                    # and send the message
                    client_socket.send(msg.encode())
            elif opcode == OPCODE_ILLEGAL_OPCODE:
                pass #maybe kick the offending client

while True:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    # add the new connected client to connected sockets
    client_sockets.add(client_socket)
    # start a new thread that listens for each client's messages
    t = Thread(target=listen_for_client, args=(client_socket,))
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()
	#close client sockets
    #for cs in client_sockets:
   #		cs.close()
   # s.close()
