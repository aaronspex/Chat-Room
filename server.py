import socket

PORT = 1337
HOST = "127.0.0.1"

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", PORT))

clients = []
nicknames = []

print(f"Waiting on port: {PORT}")

def addUser(data, addr):
    clients.append(addr)
    nicknames.append(data)
    print(f"NEW USER: {data}, {addr}")


def parseChat(rawMsg, addr):
    msg = rawMsg.decode('utf-8')
    if msg[1:4] == "com":
        if msg[5:9] == "JOIN":
            addUser(msg.split(",")[2], msg.split(",")[3])
    else:
        print(f"CHAT RECIEVED: {msg}")





#{com,JOIN,NICKNAME,HOSTNAME}
#{cha:NICKNAME CHAT-CONTENTS}

while True:
    data, addr = s.recvfrom(1024)
    parseChat(data, addr)
