import socket
import random
import threading
host = "127.0.0.1"
port = random.randint(1024,65534)
SERVER_PORT = 1337
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

print("PLEASE ENTER IN A NICKNAME IN ORDER TO JOIN THE CHATROOM!\n")
nickname = input("Enter Nickname Here: ")
s.sendto(f"[com,JOIN,{nickname},{host},{port},]".encode('utf-8'), (host,SERVER_PORT))



def send():        
    while True:
        msg = input('Message to send: ')
        parseChat(msg)

def displayChat(chat):
    print("\n",chat.split(",")[2],"\n")



def receive():
    while True:
        data, addr = s.recvfrom(1024)
        displayChat(data.decode('utf-8'))

def parseChat(msg):
    chat = f"[cha,{nickname},{msg},]"
    s.sendto(chat.encode('utf-8'), (host,SERVER_PORT))
    
    

#t1 = threading.Thread(target = send, args=())
#t1.start()

t2 = threading.Thread(target = receive, args = ())
t2.start()


t1 = threading.Thread(target = send, args=())
t1.start()

