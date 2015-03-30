import socket
import sys
import threading
import client
import server
import graph
import pickle
import atexit
import os
import random

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
        self.node = None
        self.client = None
        self.network = None
        self.dc = None
        self.username = None
        self.propagationChannel = []
        random.seed()
        self.launchApp()

    def launchApp(self):
        top = Toplevel(self.parent)
        top.title("Username:")
        top.grab_set()
        port = Entry(top)
        port.grid(row=1, column=1)
        port.focus_set()
        go = Button(top, text="Launch", command=lambda: self.setName(port.get(), top))
        go.grid(row=2, column=1)

    def initUI(self):
        self.parent.title("ChatApp")
        self.pack(fill=BOTH, expand=1)
        


        # buttons for remote client connections
        buttonsFrame = Frame(self)
        exitButton = Button(buttonsFrame, text="Disconnect & Exit", command=lambda: self.exitApp())
        remoteHostButton = Button(buttonsFrame, text="Connect Remotely", command=lambda: self.exitApp())
        exitButton.grid(row=0, column=1)
        remoteHostButton.grid(row=0, column=2)
        buttonsFrame.pack()

        chatFrame = Frame(self, relief=RAISED, borderwidth=1)
        chatTopFrame = Frame(chatFrame) 
        self.chatText = Text(chatTopFrame)
        chatScroll = Scrollbar(chatTopFrame)
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
        
        # the fun starts here
        master_serv = server.Server(self)
        master_serv.start()
        self.server = master_serv 
        self.after(500, lambda: self.declarePortNum())
        self.after(100, lambda: self.uclient_init())
        self.after(1500, lambda: self.isLocalInstance(self.port))
        self.after(2000, lambda: self.retrieveGraph())
        self.after(3000, lambda: self.app_connect())

    def setName(self, username, window):
        self.username = username
        self.initUI()
        window.destroy()
    
    def declarePortNum(self):
        self.writeOutput("ChatApp is waiting on port: " + str(self.port)) 

    # initiates the search for local instances
    def uclient_init(self):
        self.findInstance = client.udpClient()
        self.findInstance.start()
        self.writeOutput("Looking for existing instances.....please wait")

    # determine if there is a local instance
    def isLocalInstance(self, port):
        (addr, cport, success) = self.findInstance.search
        if success:
            self.writeOutput("Found existing instance at: " + addr +':'+cport)
            # import the existing graph structure if found
            self.dconnect(addr, int(cport))
        else:
            self.writeOutput("No existing instance found!") 
            self.writeOutput("Starting broadcast for this instance...")
            self.findInstance = None
            self.broadcast = server.udpServer(port, self)
            self.broadcast.start()
    
    # connecting using the graph retrieval client
    def dconnect(self, addr, port):
        if self.dc is None:
            serv = client.dClient(self, addr, port)
            serv.start()
            self.dc = serv
        else:
            self.writeOutput("GG")

    #retrieving graph
    def retrieveGraph(self):
        if self.dc:
            self.dc.sock.send('retrievelegbat')
        else:
            self.network = graph.NetGraph(self,{self.node: []}, [] )
        self.writeOutput("Thanks for your patience - Your ChatApp is read to use!")
        self.writeOutput("...Remember to disconnect properly!")

    # for actual connections 
    def app_connect(self):
        addr_lst = []
        port_lst = []
        # need to write a real way to ping instead of current implementation, will fix later...
        edge_lst = []
        pings = []
        if self.dc:
            for node in self.dc.retrieved[0]:
                ad = node.split('::')[0]
                pings.append((ad, random.uniform(0.0,25.0)))
                port_lst.append(int(node.split('::')[1]))
            edge_lst = self.dc.retrieved[1]
                
            pings.sort()

            serv = client.Client(self, pings, port_lst, edge_lst)
            serv.start()
            self.client = serv

    # safe exit, hopefully
    def exitApp(self):
        self.network.lost_connection(self.node)
        self.server.send_through_server('exitc0d3'+self.node)
        if self.client:
            self.client.sendMsg('exitc0d3'+self.node)

        for process in [self.broadcast, self.server, self.client]:
            if process:
                process.isOn = 0
        del self.chatText
        del self.findInstance
        del self.broadcast
        del self.server
        del self.client
        del self.network
        sys.exit(1)
        os._exit(1)
        self.parent.destroy()

    # sends messages for propagation
    def clearField(self, text, clearField):
        clearField
        self.writeOutput("<you> : " + text)
        if self.client:
            self.client.sendMsg(text)
        if self.server:
            self.server.send_through_server(text)

    # write to chat box
    def writeOutput(self, text):
        self.chatText.config(state=NORMAL)
        self.chatText.insert(END, '\n')
        self.chatText.insert(END, text)
        self.chatText.yview(END)
        self.chatText.config(state=DISABLED)

    # a convoluted way of getting the ping
    def ping_addr(self, addr):
        result = subprocess.Popen(["ping", "-c", "1", addr], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
        out, error = result.communicate()
        out1 = out.split("time=")
        if out1[1]:
            ping = float(out1[1].split(" ms\n")[0])
            self.writeOutput(str(ping))
            return ping+random.uniform(0.0,25.0)
        else:
            return random.uniform(0.0,100.0)
            
#-----------------------------------------------------------------------------------#
def main():
    root = Tk()
    root.geometry("1200x700+300+300")
    app = NetAppGUI(root)
    root.mainloop()
    def safe_close():
        app.exitApp()    
    # ensures all sockets are closed
    atexit.register(safe_close)

if __name__ == '__main__':
    main()
   
