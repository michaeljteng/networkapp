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
        self.client = None
        self.initUI()

    
    def initUI(self):
        self.parent.title("Chat Client")
        self.pack(fill=BOTH, expand=1)

        # set up a menubar for the commands: File, Network, Graph
        menubar = Menu(self)
        self.parent.config(menu=menubar)

        # file menu
        fileMenu = Menu(menubar)
        # adding commands to the file menu
        fileMenu.add_command(label='Exit', command=lambda: self.nothing())
        menubar.add_cascade(label="File", menu=fileMenu)

        # network menu
        networkMenu = Menu(menubar)
        # adding commands to the file menu
        networkMenu.add_command(label='Host a Server', 
                                command=lambda: self.server_init())
        networkMenu.add_command(label='Connect to Server', 
                                command=lambda: self.connect())
        networkMenu.add_command(label='Discover Instances', 
                                command=lambda: self.uclient_init())
        menubar.add_cascade(label="Network", menu=networkMenu)

        # graph menu
        graphMenu = Menu(menubar)
        # adding commands to the file menu
        graphMenu.add_command(label='Run MST', command=self.nothing)
        graphMenu.add_command(label='Name Search', command=self.nothing)
        graphMenu.add_command(label='Pathfinder', command=self.nothing)
        menubar.add_cascade(label="File", menu=graphMenu)

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
        self.chatText.insert(END, "fuck cs2")
        self.chatText.config(yscrollcommand=chatScroll.set, state=DISABLED)
        chatFrame.pack(side=LEFT, fill=BOTH)

        networkGraph = graph.NetGraph(self)
        self.after(1000, lambda: self.uclient_init())
        self.after(7500, lambda: self.no())
#        self.ping('192.168.1.8')
              #c = client.Client('',10000)
        #c.start()

    def nothing(self):
        print "nothing"

    def server_init(self):
        serv = server.Server(self)
        serv.start()
        self.server = serv

    def connect(self):
        if self.client is None:
            serv = client.Client(self)
            serv.start()
            self.client = serv 
        else:
            self.writeOutput("u dumbfuk")
    # the udp broadcast for instance discovery
    def broadcast_server(self, master):
        top = Toplevel(master)
        top.title("host a broadcast server")
        top.grab_set()
        Label(top, text="Port:").grid(row=0)
        port = Entry(top)
        port.grid(row=0, column=1)
        port.focus_set()
        go = Button(top, text="Launch", command=lambda: self.userver_init(top))
        go.grid(row=1, column=1)

    def userver_init(self, window):
        serv = server.udpServer()
        serv.start()
        window.destroy()

    def uclient_init(self):
        self.findInstance = client.udpClient()
        self.findInstance.start()
        self.writeOutput("looking for existing instances.....please wait")
    
    def no(self):
        (addr, success) = self.findInstance.search
        if success:
            self.writeOutput("found existing instance at: " + addr)
        else:
            self.writeOutput("no existing instance found - starting broadcast option")
        self.findInstance = None
        self.broadcast = server.udpServer()
        self.broadcast.start()

       
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
        if self.server:
            self.server.send_through_server(text)


    def writeOutput(self, text):
        self.chatText.config(state=NORMAL)
        self.chatText.insert(END, '\n')
        self.chatText.insert(END, "bitch says?...")
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
   
