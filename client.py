import socket
import random
host = "127.0.0.1"
port = 1337
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seshID = random.randint(1000, 9998)

print("PLEASE ENTER IN A NICKNAME IN ORDER TO JOIN THE CHATROOM!\n")
nickname = input("Enter Nickname Here: ")
s.sendto(f"[com,JOIN,{nickname},{host}".encode('utf-8'), (host,port))


while True:
    msg = input('Message to send: ')
    s.sendto(msg.encode('utf-8'), (host, port))
