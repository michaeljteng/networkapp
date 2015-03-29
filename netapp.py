import socket
import sys
import threading
import client
import server
import graph

if not sys.hexversion > 0x03000000:
    from Tkinter import *
else:
    from tkinter import *

from time import sleep

import subprocess

class NetAppGUI(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent) #background='white'#
        self.parent = parent
        self.chatText = None
        self.findInstance = None
        self.broadcast = None
        self.server = None
        self.port = None
        self.client = None
        self.initUI()

    
    def initUI(self):
        self.parent.title("Chat Client")
        self.pack(fill=BOTH, expand=1)

        # buttons for remote client connections
        buttonsFrame = Frame(self)
        exitButton = Button(buttonsFrame, text="Disconnect & Exit", command=lambda: self.nothing())
        remoteHostButton = Button(buttonsFrame, text="Connect Remotely", command=lambda: self.nothing())
        serverb = Button(buttonsFrame, text="server", command=lambda: self.serverPrompt(self.parent))
        cb = Button(buttonsFrame, text="client", command=lambda:self.connect())
        exitButton.grid(row=0, column=1)
        remoteHostButton.grid(row=0, column=2)
        serverb.grid(row=0, column=3)
        cb.grid(row=0, column=4)
        buttonsFrame.pack()

        # add a new frames to seperate the visualization and chat
        chatFrame = Frame(self, relief=RAISED, borderwidth=1)
        chatTopFrame = Frame(chatFrame) 
        # a text widget for the chat
        self.chatText = Text(chatTopFrame)
        # a scrollbar for the chat
        chatScroll = Scrollbar(chatTopFrame)
        # a place to input text and or commands
        
        chatTopFrame.pack(side=TOP, expand=1, fill=BOTH)
        inputText = Entry(chatFrame, borderwidth=1)
        inputText.bind("<Return>", lambda event: self.clearField(inputText.get(), inputText.delete(0, END)))
        inputText.delete(0, END)

        self.chatText.pack(side=LEFT, fill=Y)
        chatScroll.pack(side=RIGHT, fill=Y)
        inputText.pack(side=BOTTOM, fill=BOTH)

        chatScroll.config(command=self.chatText.yview)
        self.chatText.insert(END, "Welcome to the Chat Client!")
        self.chatText.config(yscrollcommand=chatScroll.set, state=DISABLED)
        chatFrame.pack(side=LEFT, fill=BOTH)
        networkGraph = graph.NetGraph(self)

        # The fun starts here
        master_serv = server.Server(self)
        master_serv.start()
        self.server = master_serv 
        self.after(500, lambda: self.declarePortNum())
        self.after(1000, lambda: self.uclient_init())
        self.after(7500, lambda: self.isLocalInstance(self.port))

#        self.ping('192.168.1.8')
              #c = client.Client('',10000)
        #c.start()

    def declarePortNum(self):
        self.writeOutput("ChatApp is waiting on port: " + str(self.port)) 

    def userver_init(self, window):
        serv = server.udpServer()
        serv.start()
        print self.server.port
        window.destroy()


    def uclient_init(self):
        self.findInstance = client.udpClient()
        self.findInstance.start()
        self.writeOutput("Looking for existing instances.....please wait")
    
    def isLocalInstance(self, port):
        (addr, cport, success) = self.findInstance.search
        if success:
            self.writeOutput("Found existing instance at: " + addr +':'+cport)
            self.connect(addr, int(cport))
        else:
            self.writeOutput("No existing instance found!") 
            self.writeOutput("Starting broadcast for this instance...")
            self.findInstance = None
            print "STARTING" +str(port)
            self.broadcast = server.udpServer(port)
            self.broadcast.start()
        self.writeOutput("Thanks for your patience - Your ChatApp is read to use!") 
    def nothing(self):
        print "nothing"

    def server_init(self, addr, port, window):
        serv = server.Server(self, addr)
        serv.start()
        self.server = serv
        if window:
            window.destroy()

    def connect(self, addr, port):
        self.writeOutput("Connecting to the discovery!")
        if self.client is None:
            serv = client.Client(self, addr, port)
            serv.start()
            self.client = serv 
        else:
            self.writeOutput("u dumbfuk")

    # the udp broadcast for instance discovery
    def serverPrompt(self, master):
        top = Toplevel(master)
        top.title("Custom Server")
        top.grab_set()
        Label(top, text="Addr:").grid(row=0)
        port = Entry(top)
        port.grid(row=0, column=1)
        port.focus_set()
        Label(top, text="Port:").grid(row=1)
        port2 = Entry(top)
        port2.grid(row=1, column=1)
        port2.focus_set()
        go = Button(top, text="Launch", command=lambda: self.server_init(port.get(), port2.get(), top))
        go.grid(row=2, column=1)



       
    def custom_server(self, master):
        #Launches server options window for getting port
        top = Toplevel(master)
        top.title("custom server")
        top.grab_set()
        Label(top, text="Port:").grid(row=0)
        port = Entry(top)
        port.grid(row=0, column=1)
        port.focus_set()
        go = Button(top, text="Launch", 
                    command=lambda: self.server_init(port.get(), top))
        go.grid(row=1, column=1)

    def clearField(self, text, clearField):

        # probably a better way to do this, but i'm being lazy
        # thank god python is functional
        # yes, this is really all that is happening does....
        clearField
        self.writeOutput("....." + text)
        if self.client:
            self.client.sendMsg(text)
        #if self.server:
         #   self.server.send_through_server(text)


    def writeOutput(self, text):
        self.chatText.config(state=NORMAL)
        self.chatText.insert(END, '\n')
        self.chatText.insert(END, text)
        self.chatText.yview(END)
        self.chatText.config(state=DISABLED)

    # a convoluted way of getting the ping
    def ping(self, addr):
        result = subprocess.Popen(["ping", "-c", "1", addr], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
        out, error = result.communicate()
        out1 = out.split("time=")
        if out1[1]:
            ping = float(out1[1].split(" ms\n")[0])
            self.writeOutput(str(ping))
            
#-----------------------------------------------------------------------------------#
def main():
    root = Tk()
    root.geometry("1000x600+300+300")
    app = NetAppGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
   
