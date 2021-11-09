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
    clients.append((addr, port))
    nicknames.append(nickname)

    print(f"NEW USER: {nickname}, ({addr}, {port})")
    print(clients)

def broadcast(sender, message):
    chat = f"[cha,{sender},{message},]"
    for client in clients:
        hostname = client[0]
        sendPort = client[1]
        print(hostname, sendPort)
        s.sendto(chat.encode('utf-8'), (client[0], int(client[1])))
        print(f"hostname: {hostname}, port: {sendPort}")



def parseChat(rawMsg, addr):
    msg = rawMsg.decode('utf-8')
    splitMsg = msg.split(",")
    if msg[1:4] == "com":
        if msg[5:9] == "JOIN":
            addUser(splitMsg[2], splitMsg[3], splitMsg[4])
    else:
        print(f"CHAT RECIEVED: {msg}")
        print(splitMsg[1], splitMsg[2])
        broadcast(splitMsg[1], splitMsg[2])





#[com,JOIN,NICKNAME,HOSTNAME,PORT,]
#[cha,NICKNAME CHAT-CONTENTS,]

while True:
    data, addr = s.recvfrom(1024)
    parseChat(data, addr)
