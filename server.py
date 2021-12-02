import socket
import random
PORT = 1337
HOST = "127.0.0.1"

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", PORT))

clients = []
nicknames = []

print(f"Waiting on port: {PORT}")

def addUser(nickname, addr, port):
    #If a user already has that nickname, slap a random number onto it and rejoin
    #if nickname in nicknames:
        #addUser(f"{nickname}{random.randint(0,9)}", addr, port)
    #else:
    unicast("usrl"+str(nicknames), addr, int(port))
    clients.append((addr, port))
    nicknames.append(nickname)
    broadcast(f"usrj{nickname}")
    print(f"NEW USER: {nickname}, ({addr}, {port})")

def removeUser(nickname):
    print(f"USER LEFT:{nickname},{clients[nicknames.index(nickname)]}")
    userNdx = nicknames.index(nickname)
    del nicknames[userNdx]
    del clients[userNdx]
    broadcast(f"usrr{nickname}")
    broadcast(f"cha{nickname} has left the chatroom...")

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
