import socket
import random
PORT = 1337
HOST = "127.0.0.1"

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", PORT))

clients = []
nicknames = []

print(f"Waiting on port: {PORT}")

#allows a new user to join the chatroom
def addUser(nickname, addr, port):
    #If a user already has that nickname, append a random number onto 
    #the nickname and repeat recursively until the nickname is unique
    if nickname in nicknames:
        addUser(f"{nickname}{random.randint(0,9)}", addr, port)
    
    else:

        #Let the new user know their final nickname. The server has to do this because 
        #the new user's final nickname may end up being different from the nickname 
        #they requested in the case an existing user already has the nickname that the new user requested
        unicast(f"nic{nickname}", addr, int(port))

        #Send the new user that joined the list of other users connected to the chatroom
        unicast("usrl"+str(nicknames), addr, int(port))

        #Add the user to the list of active users
        clients.append((addr, port))
        nicknames.append(nickname)

        #Notify the other clients that a new user has joined
        broadcast(f"usrj{nickname}")
        broadcast(f"cha***{nickname} has joined the server***")

        #Send the user that joined a welcome message
        unicast(f"cha***Welcome To The Chatroom {nickname}***", addr, int(port))
    
        #Log to server that a new user joined
        print(f"NEW USER: {nickname}, ({addr}, {port})")

#Removes a specified user from the chatroom
def removeUser(nickname):
    #First check if the specified user exists
    if nickname in nicknames:
        #Log to server that the user left
        print(f"USER LEFT:{nickname},{clients[nicknames.index(nickname)]}")
        
        #Find the index that the user is at in the user arrays and delete them
        userNdx = nicknames.index(nickname)
        del nicknames[userNdx]
        del clients[userNdx]
        
        #broadcast to all clients that the specified user has left
        broadcast(f"usrr{nickname}")
        broadcast(f"cha***{nickname} has left the chatroom***")

    else:
        print(f"ERROR: USER '{nickname}' DOES NOT EXIST AND CAN'T BE REMOVED")

#Send message to all clients currently connected to the server
def broadcast(msg):
    for client in clients:
        hostname = client[0]
        sendPort = client[1]
        s.sendto(msg.encode('utf-8'), (client[0], int(client[1])))

#Send message to a specific client
def unicast(msg, addr, port):
    s.sendto(msg.encode('utf-8'), (addr, port))
    
def parseChat(rawMsg, addr):
    msg = rawMsg.decode('utf-8')
    splitMsg = msg[3:].split(",")
    if msg[0:3] == "joi":
        addUser(splitMsg[0], splitMsg[1], splitMsg[2])
    elif msg[0:3] == "cha":
        print(f"CHAT RECIEVED: {msg[3:]}")
        broadcast(msg)
    elif msg[0:3] == "lea":
        removeUser(splitMsg[0])

while True:
    data, addr = s.recvfrom(1024)
    parseChat(data, addr)
