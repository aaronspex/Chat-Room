import socket
import random


PORT = 1337
HOST = "127.0.0.1"

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", PORT))

clients = []
nicknames = []

print(f"Waiting on port: {PORT}")

def addUser(data, addr):
    seshID = random.randint(1000,9998)
    s.sendto(seshID, (HOST, PORT))
    clients.append((addr, seshID))
    nicknames.append(data)

    print(f"NEW USER: {data}, {addr}")
    print(clients)

def broadcast(sender, message):
    chat = f"[cha,{sender},{message},]"
    for client in clients:
        s.sendto(chat.encode('utf-8'), (client[0], PORT))



def parseChat(rawMsg, addr):
    msg = rawMsg.decode('utf-8')
    splitMsg = msg.split(",")
    if msg[1:4] == "com":
        if msg[5:9] == "JOIN":
            addUser(splitMsg[2], splitMsg[3])
    else:
        print(f"CHAT RECIEVED: {msg}")
        broadcast(splitMsg[1], splitMsg[2])





#[com,JOIN,NICKNAME,HOSTNAME,]
#[cha,NICKNAME CHAT-CONTENTS,]

while True:
    data, addr = s.recvfrom(1024)
    parseChat(data, addr)
