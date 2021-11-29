from tkinter import *
from tkinter import ttk
import threading
import random
import socket
import queue

#Initialize UDP socket
host = "127.0.0.1"
port = random.randint(1024,65534) #choose a random port to communicate to the server over
SERVER_PORT = 1337
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

#Sentinal value used for receiveThread/GUI communication
global done 
done = False
#Queue for chats
chatQueue = queue.Queue()

#Receives chats and adds them to the queue for the GUI to proccess
def receiveChat():
    global done
    while not done:
        data, addr = s.recvfrom(1024) #blocking call
        msg = data.decode('utf-8')
        chatQueue.put(msg)

receiveThread = threading.Thread(target = receiveChat, args = ())
receiveThread.start()

class chatGui:
    def __init__(self, root):
        #Initialize the main frame the GUI will use
        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.initGUI(self.mainframe)

    #Initializes GUI Widgets and displays the join screen
    def initGUI(self, frame):
        #Define GUI elements related to join screen
        self.nickname = StringVar()
        self.nickname_entry = ttk.Entry(self.mainframe, width = 7, textvariable=self.nickname)
        self.nickname_entry.grid(column = 0, row = 0)
        self.joinButton = ttk.Button(self.mainframe, text = 'join', command = self.joinRoom)
        self.joinButton.grid(column = 1, row = 0)

        #Define GUI elements related to chat room screen
        self.text = Text(self.mainframe, width=40, height=10, state=DISABLED)
        self.message = StringVar()
        self.sendButton = ttk.Button(self.mainframe, text = "send", command = self.sendChat)
        self.message_entry = ttk.Entry(self.mainframe, width = 7, textvariable=self.message)

        #Put padding around GUI elements
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        #Remove the GUI elements that are specific to the chat room screen
        self.text.grid_remove()
        self.sendButton.grid_remove()
        self.message_entry.grid_remove()  

        #Tells tkinter to run the function "onClosing" when the client is closed
        root.protocol("WM_DELETE_WINDOW", self.onClosing)

        #Tell tkinter to start running the updateChatbox method w/o causing a blocking call
        root.after(0, self.updateChatbox)

    def joinRoom(self):
        name = self.nickname.get()
        s.sendto(f"[com,JOIN,{name},{host},{port},]".encode('utf-8'), (host,SERVER_PORT))
        self.nickname_entry.grid_remove()
        self.joinButton.grid_remove()
        self.message_entry.grid(column = 0, row =1, sticky=(W,E))
        self.sendButton.grid(column=1, row = 1, sticky=(W,E))
        self.text.grid(column = 0, row = 0)

    def sendChat(self):
        chat = chat = f"[cha,{self.nickname.get()},{self.message.get()},]"
        s.sendto(chat.encode('utf-8'), (host,SERVER_PORT))

    #Checks the chatQueue and populates the chatbox with any new chats
    def updateChatbox(self):
        while not chatQueue.empty():
            self.text.config(state=NORMAL)
            self.text.insert(END, chatQueue.get()+"\n")
            self.text.config(state=DISABLED)
        #Tell tkinter to run this function again in 500ms
        root.after(500, self.updateChatbox)

    
    #Allows the GUI and seperate receive thread to exit gracefully  
    def onClosing(self):
        #done is the var that allows GUI to signal to thread that user wants to exit
        global done
        done = True
        #Destory GUI window
        root.destroy()
        #Send some data to ourselves to move past the blocking call and terminate "while True" loop in receive thread
        s.sendto("HALT".encode('utf-8'), ('127.0.0.1', port))



#Launches GUI
root = Tk()
chatGui(root)
root.mainloop()
