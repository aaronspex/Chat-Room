from tkinter import *
from tkinter import ttk
import threading
import random
import socket


host = "127.0.0.1"
port = random.randint(1024,65534)
SERVER_PORT = 1337
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
class chatGui:

    def __init__(self, root):

        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.nickname = StringVar()
        self.nickname_entry = ttk.Entry(self.mainframe, width = 7, textvariable=self.nickname)
        self.nickname_entry.grid(column = 0, row = 0)
        self.joinButton = ttk.Button(self.mainframe, text = 'join', command = self.joinRoom)
        self.joinButton.grid(column = 1, row = 0)

        self.text = Text(self.mainframe, width=40, height=10, state=DISABLED)
        self.message = StringVar()
        self.sendButton = ttk.Button(self.mainframe, text = "send", command = self.sendChat)
        self.message_entry = ttk.Entry(self.mainframe, width = 7, textvariable=self.message)

#        for child in self.mainframe.winfo_children(): 
#            child.grid_configure(padx=5, pady=5)

        self.setupThreads()

    def joinRoom(self):
        name = self.nickname.get()
        s.sendto(f"[com,JOIN,{name},{host},{port},]".encode('utf-8'), (host,SERVER_PORT))
#        self.text = Text(self.mainframe, width=40, height=10, state=DISABLED)
#        self.message = StringVar()
#        self.sendButton = ttk.Button(self.mainframe, text = "send", command = self.sendChat)
#        self.message_entry = ttk.Entry(self.mainframe, width = 7, textvariable=self.message)
        self.nickname_entry.grid_remove()
        self.joinButton.grid_remove()
        self.message_entry.grid(column = 0, row =1, sticky=(W,E))
        self.sendButton.grid(column=1, row = 1, sticky=(W,E))
        self.text.grid(column = 0, row = 0)

    def sendChat(self):
        chat = chat = f"[cha,{self.nickname.get()},{self.message.get()},]"
        s.sendto(chat.encode('utf-8'), (host,SERVER_PORT))



    def receiveChat(self):
        while True:
            data, addr = s.recvfrom(1024)
            datum = data.decode('utf-8')
            self.text.config(state=NORMAL)
            print(datum, " should be added")
            self.text.insert(END, datum+"\n")




    #probably wont need to use this one
    def displayChat(self, msg):
        self.text.config(state=NORMAL)
        print(msg, " should be added")
        self.text.insert(END, msg+"\n")

    def setupThreads(self):
        receiveThread = threading.Thread(target = self.receiveChat, args = ())
        receiveThread.start()

        #sendThread = threading.Thread(target = sendChat, args = ())
        #sendThread.start()



    

root = Tk()
chatGui(root)
root.mainloop()

def sendNick(msg):
    s.sendto(f"[com,JOIN,{msg},{host},{port},]".encode('utf-8'), (host,SERVER_PORT))

def send(msg):
    parseChat(msg)

def displayChat(chat):
    print("\n",chat.split(",")[2],"\n")

def receive():
    while True:
        print("That Shits Bananas")
        #data, addr = s.recvfrom(1024)
        #chatGui.displayChat(chatGui, data.decode('utf-8'))

def parseChat(msg): 
    s.sendto(chat.encode('utf-8'), (host,SERVER_PORT))


#guiThread = threading.Thread(target = __main__, args = ())
#guiThread.start()

recieveThread = threading.Thread(target = receive, args = ())
recieveThread.start()
