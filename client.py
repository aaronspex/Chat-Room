#Client.py: Client for a UDP socket based chatroom
#Aaron Spexarth, 12/5/21
import tkinter as tk
from tkinter import *
from tkinter import ttk
import threading
import random
import socket
import queue

#Initialize and configure udp socket
host = "127.0.0.1"
port = random.randint(1024,65534) #choose a random port to communicate with the server over
SERVER_PORT = 1337
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

#Sentinel value used by the GUI and Receive Threads to communicate
#when the user wants to quit the program
global done 
done = False

#Queue for messages from the server, allows the GUI and receive thread to communicate
messageQueue = queue.Queue()

#Receives messages and adds them to the queue for the GUI to proccess
def receiveMessages():
    global done
    while not done:
        data, addr = s.recvfrom(1024)
        msg = data.decode('utf-8') 
        messageQueue.put(msg)

receiveThread = threading.Thread(target = receiveMessages, args = ())
receiveThread.start()


class chatGui:
    def __init__(self, root):
        #Initialize the main frame the GUI will use
        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.initGUI(self.mainframe)
        root.title("Chatroom")
        root.geometry('250x50+50+50')
        #Holds the nickname of the user
        self.nickname = None

    #Initializes GUI :Widgets and displays the join screen
    def initGUI(self, frame):
        #Define GUI elements related to join screen
        self.nickname_var = StringVar()
        self.nickname_entry = ttk.Entry(self.mainframe, width = 7, textvariable=self.nickname_var)
        self.nickname_entry.grid(column = 0, row = 0)
        self.joinButton = ttk.Button(self.mainframe, text = 'join', command = self.joinRoom)
        self.joinButton.grid(column = 1, row = 0)

        #Define GUI elements related to chat room screen
        self.text = Text(self.mainframe, width=40, height=10, state=DISABLED)
        self.message = StringVar()
        self.sendButton = ttk.Button(self.mainframe, text = "send", command = self.proccessInput)
        self.message_entry = ttk.Entry(self.mainframe, width = 7, textvariable=self.message)
        self.userList = ttk.Treeview(self.mainframe)
        self.userList.heading('#0', text = "Online Users")
        self.chatBoxScrollBar = ttk.Scrollbar(self.mainframe, command=self.text.yview)
        self.text['yscrollcommand'] = self.chatBoxScrollBar.set

        #Configure padding around GUI elements
        for child in self.mainframe.winfo_children():
            if not (child == self.chatBoxScrollBar or child == self.text):
                child.grid_configure(padx=5, pady=5)

        #Remove the GUI elements that are specific to the chat room screen
        self.text.grid_remove()
        self.sendButton.grid_remove()
        self.message_entry.grid_remove() 
        self.userList.grid_remove()
        self.chatBoxScrollBar.grid_remove()

        #Tells tkinter to run the method "onClosing" when the client is closed
        root.protocol("WM_DELETE_WINDOW", self.onClosing)

        #Tell tkinter to start running the processMessages method w/o causing a blocking call
        root.after(0, self.processMessages)
        
        #Bind the enter key to click the join room button
        root.bind('<Return>', lambda event : self.joinRoom())

    #Goes through the process of connecting the user to the chatroom
    def joinRoom(self):
        #If the user has not entered in anything for the 
        #nickname do not proceed, end the method
        if not self.nickname_var.get():
            return

        #Resize screen
        root.geometry('650x300+50+50')

        #Let server know we would like to join
        s.sendto(f"joi{self.nickname_var.get()},{host},{port}".encode('utf-8'), (host,SERVER_PORT))

        #Reconfig GUI to show chatroom screen
        self.nickname_entry.grid_remove()
        self.joinButton.grid_remove()
        self.message_entry.grid(column = 0, row =1, sticky=(W,E))
        self.sendButton.grid(column=1, row = 1, sticky=(W,E))
        self.text.grid(column = 0, row = 0, sticky=(N,S,E,W))
        self.userList.grid(column = 2, row = 0)
        self.chatBoxScrollBar.grid(column = 1, row = 0, sticky=(N,W,S))

        #Rebind the enter key to the send button
        root.bind('<Return>', lambda event : self.proccessInput())




    def proccessInput(self):
        messageContents = self.message.get()
        #Make sure the user actually typed something in the chatbox
        if len(messageContents) >= 1:
            if messageContents == "/q":
                self.onClosing()

            elif messageContents == "/h":
                messageQueue.put("cha*****************Help*******************\n'/pm user' to private message a user\n'/c' to clear the chatbox\n'/q' to quit")
                self.message_entry.delete(0, END)

            elif messageContents == "/c":
                self.text.config(state=NORMAL)
                #Clear the chatbox
                self.text.delete("1.0", END)
                #Scroll the chatbox down to the most recent down
                self.text.see("end")
                #Set the chatbox back to DISABLED mode so that it cant be written to by the user
                self.text.config(state=DISABLED)
                self.message_entry.delete(0, END)

            elif messageContents[0:4] == "/pm " and len(messageContents) > 4:
                self.sendPM(messageContents[4:])

            elif messageContents[0] == "/":
                messageQueue.put("cha****UNKNOWN COMMAND DO '\h' FOR HELP****")
                self.message_entry.delete(0, END)
            else:
                self.sendChat()

    #Sends a PM to a user
    def sendPM(self, contents):
        #seperate the original command into receiver and message
        splitContents = contents.split(" ", 1)
        #If user provided receiver and message continue, otherwise show error message
        if len(splitContents) == 2:
            receiver = splitContents[0]
            message = splitContents[1]
            sender = self.nickname
       
            #If the user is online and the user is not trying to send a PM to themselves, send the PM
            if self.isUserOnline(receiver) and receiver != self.nickname:
                pm = f"pvm{receiver},{sender},{message}"
                s.sendto(pm.encode('utf-8'), (host,SERVER_PORT))

            elif receiver == self.nickname:
                messageQueue.put("cha********YOU CANT PM YOURSELF :( *******")
            else:
                messageQueue.put("cha***CANT SEND(RECIPENT DOES NOT EXIST)***")
        else:
            messageQueue.put("cha**********USAGE: /PM USER MSG**********")
        self.message_entry.delete(0, END)

    #Returns true if the specified user is online
    def isUserOnline(self, user):
        #Search through the treeview userList widget and search for the user
        for record in self.userList.get_children():
            if self.userList.item(record)['text'] == user:
                return True
        return False

    #Sends a chat to the server
    def sendChat(self):
        chat = f"cha{self.nickname}: {self.message.get()}"
        s.sendto(chat.encode('utf-8'), (host,SERVER_PORT))
        self.message_entry.delete(0, END)

    #Proccesses messages from the messageQueue and performs the appropriate
    #action based on the message type
    def processMessages(self):
        #While there are messages waiting in the queue to be processed
        #continue processing them
        while not messageQueue.empty():
            msg = messageQueue.get()

            #if the msg is a chat, display it appropriately
            if msg[0:3] == "cha":
                self.displayChat(msg[3:])

            #If the message is a userList action, pass it to the correct method
            elif msg[0:3] == "usr":
                self.updateUserList(msg[3:])

            #If the message contains the user's finalized nickname, pass it to the correct method
            elif msg[0:3] == "nic":
                self.setNickname(msg[3:])

        #Tell tkinter to run this function again in 500ms
        root.after(500, self.processMessages)

    #Sets the user's nickname
    def setNickname(self, nickname):
        self.nickname = nickname
        
    #Displays the given chat to the chatbox
    def displayChat(self, chat):
        #Set the chatbox to NORMAL mode so the chat can be written to it
        self.text.config(state=NORMAL)
        #Write the chat to the chatbox
        self.text.insert(END, chat+"\n")
        #Scroll the chatbox down to the most recent chat
        self.text.see("end")
        #Set the chatbox back to DISABLED mode so that it cant be written to by the user
        self.text.config(state=DISABLED)


    #Deletes the specified user from the userList
    def deleteUserFromUserList(self, user):
        #Loop through the userList until we find the specified user, then delete it
        for record in self.userList.get_children():
            if self.userList.item(record)['text'] == user:
                self.userList.delete(record)

    #Takes in a userList message and performs the specified action
    def updateUserList(self, action):
        #if action is a list we want to add all of the users in the list to the user list
         if action[0] == "l":
            usersToAdd = eval(action[1:])
            for user in usersToAdd:
                self.userList.insert('', 'end', text = user)
         #j = user joined(add the user to the userList)
         elif action[0] == 'j':
            self.addUserToUserList(action[1:])
         #r = user left(remove the user from the userList)
         elif action[0] == 'r' :
            self.deleteUserFromUserList(action[1:])

    #Adds a user to the userList widget
    def addUserToUserList(self, username):
        #If the user we are trying to add is ourselves make that entry look special
        if(self.nickname == username):
            self.userList.insert('', 'end', text = username+' (you)', tags=('u'))
            self.userList.tag_configure('u', background = '#CFCFCF')
        else:
            self.userList.insert('', 'end', text=username)

    #Allows the GUI and seperate receive thread to exit gracefully  
    def onClosing(self):
        #done is the var that allows GUI to signal to thread that user wants to exit
        global done
        done = True
        #Destory GUI window
        root.destroy()
        #Let the server know we are leaving
        s.sendto(f"lea{self.nickname}".encode('utf-8'), ('127.0.0.1', SERVER_PORT))
        #Send some data to ourselves to move past the blocking call and terminate the while loop in receive thread
        s.sendto("HALT".encode('utf-8'), ('127.0.0.1', port))
        s.close()

#Launches GUI
root = tk.Tk()
chatGui(root)
root.mainloop()
