import socket
import random
import threading
host = "127.0.0.1"
port = 1337
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seshID = 0

print("PLEASE ENTER IN A NICKNAME IN ORDER TO JOIN THE CHATROOM!\n")
nickname = input("Enter Nickname Here: ")
s.sendto(f"[com,JOIN,{nickname},{host}".encode('utf-8'), (host,port))
data, addr = s.recvfrom(1024)
seshID = data



def send():        
    while True:
        msg = input('Message to send: ')
        print("DOSing Server")
        parseChat(msg)


def receive():
    while True:
        data, addr = s.recvfrom(1024)
        print(data)

def parseChat(msg):
    chat = f"[cha,{nickname},{msg},]"
    s.sendto(chat.encode('utf-8'), (host, port))
    
    

t1 = threading.Thread(target = send, args=())
t1.start()

t2 = threading.Thread(target = receive, args = ())
t2.start()
