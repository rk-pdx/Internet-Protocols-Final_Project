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
OPCODE_CLIENT_ID = 9
OPCODE_ERROR_MESSAGE = -1
OPCODE_ILLEGAL_OPCODE = -99
OPCODE_LIST_MEMBERS_ROOM = 11
OPCODE_LIST_CURR_ROOMS = 12
OPCODE_SEND_SPECIFIC = 13


# info about each of the connected client's
# key is address
# [0] = client socket
# [1] = client username
# [2] = current room
client_info = {}

# info about each room
# key is room name
# value is number of people in the room
rooms_info = {}

"""
# initialize list/set of all connected client's sockets
client_sockets = set()
"""

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
            #client_sockets.remove(cs)
        else:
            #if we received a message, parse opcode and sender address
            x = data.split(separator_token, 2)

            # if wrong args, ignore (trying to send error can cause crash)
            if(len(x) < 3):
                continue
            try:
                opcode = int(x[0])
                client_address = x[1]
                msg = x[2]
            except ValueError:
                opcode = OPCODE_ILLEGAL_OPCODE

            # make sure sender address exists
            if(client_address not in client_info):
                continue

            # KEEPALIVE MESSAGE
            if (opcode == OPCODE_KEEP_ALIVE):
                pass

            # SET USERNAME
            elif opcode == OPCODE_SET_USERNAME:
                client_info[client_address][1] = msg
                
            # CREATE ROOM
            elif opcode == OPCODE_CREATE_ROOM:
                room_name = msg
                # make sure the user is not in a room
                #if(client_info[client_address][2] != None):
                    # respond error
                #msg = f"{OPCODE_ERROR_MESSAGE}{separator_token}"\
                #    "\t<Error: you are already in a room>"
                #client_info[client_address][0].send(msg.encode())
                #continue

                # check that the room name isn't occupied
                if(room_name in rooms_info):
                    # respond error
                    msg = f"{OPCODE_ERROR_MESSAGE}{separator_token}"\
                        f"\t<Error: there's already a room with this name. Enter /join <room name> to join the room.>"
                    client_info[client_address][0].send(msg.encode())
                    continue
                
                # if all good, allow them to create room
                rooms_info[room_name] = 1
                #client_info[client_address][2] = room_name
                if (type(client_info[client_address][2]) != list):
                    client_info[client_address][2] = list()    
                client_info[client_address][2].append(room_name)

                # send success message
                msg = f"{OPCODE_BROADCAST_MESSAGE}{separator_token}"\
                    f"\t<You created room '{room_name}'>"
                client_info[client_address][0].send(msg.encode())

            # LIST ROOMS
            elif opcode == OPCODE_LIST_ROOMS:
                # store results to print into string
                res = ""
                if(len(rooms_info) == 0):
                    res = "\t<There are no rooms>"
                else:
                    for room in rooms_info:
                        res += ("\t-" + room + '\n')
                msg = f"{OPCODE_BROADCAST_MESSAGE}{separator_token}"\
                    f"{res}"
                client_info[client_address][0].send(msg.encode())

            # JOIN ROOM
            elif opcode == OPCODE_JOIN_ROOM:
                room_name = msg
                # make sure the user is not in a room
                #if(client_info[client_address][2] != None):
                    # respond error
                # msg = f"{OPCODE_ERROR_MESSAGE}{separator_token}"\
                #     "\t<Error: you are already in a room>"
                #client_info[client_address][0].send(msg.encode())
                #continue
                
                # make sure the room (msg) exists
                # note: we will need to create a list in the future
                # instead of seeing each person's room
                if(room_name not in rooms_info):
                    msg = f"{OPCODE_ERROR_MESSAGE}{separator_token}"\
                        "\t<Error: there is no room with this name>"
                    client_info[client_address][0].send(msg.encode())

                # allow them to join room
                if (client_info[client_address][2] == None):
                    client_info[client_address][2] = []
                
                client_info[client_address][2].append(room_name)
                rooms_info[room_name] += 1 # increment number of users in room
                msg = f"{OPCODE_BROADCAST_MESSAGE}{separator_token}"\
                    "\tYou have successfully joined the room."
                client_info[client_address][0].send(msg.encode())

                # tell chat room about new client
                join_msg = f"{OPCODE_BROADCAST_MESSAGE}{separator_token}"\
                    f"\t<{client_info[client_address][1]} joined the room>"
                for client in client_info:
                    if(client_info[client][2] == room_name):
                        client_info[client][0].send(join_msg.encode())

            # LEAVE ROOM
            elif opcode == OPCODE_LEAVE_ROOM:
                # if client is not in a room
                if(client_info[client_address][2] == None):
                    # respond error
                    msg = f"{OPCODE_ERROR_MESSAGE}{separator_token}"\
                        "\t<Error: you are already not in a room>"
                    client_info[client_address][0].send(msg.encode())
                    continue
                
                # remove client from room
                room_name = client_info[client_address][2]
                client_info[client_address][2] = None
                rooms_info[room_name] -= 1 # decrement number of people in room
                # if there's no more people in the room, delete it
                if(rooms_info[room_name] == 0):
                    del rooms_info[room_name]

                # send success message
                msg = f"{OPCODE_BROADCAST_MESSAGE}{separator_token}"\
                    f"\t<You left room '{room_name}'>"
                client_info[client_address][0].send(msg.encode())

                # if the client was actually in a room
                if(room_name != None):
                    leave_msg = f"{OPCODE_BROADCAST_MESSAGE}{separator_token}"\
                        f"\t<{client_info[client_address][1]} left the room>"
                    #notify chat room about the client leaving the room
                    for client in client_info:
                        if(client_info[client][2] == room_name):
                            client_info[client][0].send(leave_msg.encode())

            # SEND MESSAGE
            elif opcode == OPCODE_SEND_MESSAGE: # send message
                # replace the <SEP> 
                # token with ": " for nice printing
                msg = msg.replace(separator_token, ": ")

                # room name of the client sending the message
                room_name = client_info[client_address][2]

                # if they are not in a room
                if(room_name == None):
                    # respond error and ignore request
                    msg = f"{OPCODE_ERROR_MESSAGE}{separator_token}"\
                        "\t<Error: you are not in a room>\n"\
                        "\t  Use '/join <room name>' to join a room\n"\
                        "\t  Use '/list' to see names of available rooms"
                    client_info[client_address][0].send(msg.encode())
                    continue

                # send message to clients in same room
                for client in client_info:
                    # if the client is in the same room
                    if(client_info[client][2] == room_name):
                        client_info[client][0].send(msg.encode())

            # ILLEGAL OPCODE
            elif opcode == OPCODE_ILLEGAL_OPCODE:
                pass #maybe kick the offending client

            # OPCODE_LIST_MEMBERS_ROOM
            elif opcode == OPCODE_LIST_MEMBERS_ROOM:
                #print("Hit OPCODE_LIST_MEMBERS_ROOM")
                all_members_in_room = []
                room_name = msg

                for client in client_info:
                    if (client_info[client][2] != None):
                        for j in range(0, len(client_info[client][2])):
                            if (client_info[client][2][j] == room_name):
                                all_members_in_room.append(client_info[client][1])
                
                lemsg = f"{OPCODE_BROADCAST_MESSAGE}{separator_token}"\
                     f"\t<{all_members_in_room}"
                client_info[client_address][0].send(lemsg.encode())


            # opcode: OPCODE_LIST_CURR_ROOMS
            # purpose: Lists the current rooms that the user is in
            #
            elif opcode == OPCODE_LIST_CURR_ROOMS:
                if (client_info[client_address][2] == None):
                    msg = f"{OPCODE_ERROR_MESSAGE}{separator_token}"\
                        "\t<Error: you are not in any rooms.>\n"\
                        "\t  Use '/join <room name>' to join a room\n"
                    client_info[client_address][0].send(msg.encode())
                else:
                    curr_rooms = []
                    for i in range(0, len(client_info[client_address][2])):
                        curr_rooms.append(client_info[client_address][2][i])
                    
                    ret_msg = f"{OPCODE_BROADCAST_MESSAGE}{separator_token}"\
                        f"\t<{curr_rooms}"
                    client_info[client_address][0].send(ret_msg.encode())


            #
            #
            #
            elif opcode == OPCODE_SEND_SPECIFIC:
                #msg = msg.replace(separator_token, ": ")

                user_input = msg.split(" ",1)
                room_name = "empty"

                if (client_info[client_address][2] == None):
                    msg = f"{OPCODE_ERROR_MESSAGE}{separator_token}"\
                        "\t<Error: you cannot send a message, as you are not in any rooms.>\n"\
                        "\t  Use '/join <room name>' to join a room.\n"
                    client_info[client_address][0].send(msg.encode())

                # search for the room
                for i in range(0, len(client_info[client_address][2])):
                    if (client_info[client_address][2][i] == user_input[0]):
                        room_name = user_input[0]
                        break

                if (room_name == "empty"):
                    msg = f"{OPCODE_ERROR_MESSAGE}{separator_token}"\
                    "\t<Error: You are not in the room that you requested.>\n"\
                    "\t  Use '/join <room name>' to join a room.\n"
                    client_info[client_address][0].send(msg.encode())        
                else:          
                    msg = user_input[1]
                    for client in client_info:
                       for i in range(0, len(client_info[client][2])):
                            if (client_info[client][2][i] == room_name):
                                client_info[client][0].send(msg.encode())


while True:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")

    # add the new connected client to list of users
    client_address = str(client_address)
    if(client_address not in client_info):
        client_info[client_address] = [client_socket, 'Unnamed user', None]

    # send a message back with assigned client ID (just the client_address)
    msg = f"{OPCODE_CLIENT_ID}{separator_token}{client_address}"
    client_socket.send(msg.encode())

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
