import socket
import sys
import threading
import client
import server
import graph
import pickle
import atexit
import os

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
        self.launchApp()

    def launchApp(self):
        top = Toplevel(self.parent)
        top.title("Welcome to ChatApp")
        top.grab_set()
        Label(top, text="Pick a username:").grid(row=0)
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
        
        # The fun starts here
        master_serv = server.Server(self)
        master_serv.start()
        self.server = master_serv 
        self.after(500, lambda: self.declarePortNum())
        self.after(1000, lambda: self.uclient_init())
        self.after(7500, lambda: self.isLocalInstance(self.port))
        self.after(8000, lambda: self.retrieveGraph())
        self.after(8500, lambda: self.app_connect())
#        self.ping('192.168.1.8')
              #c = client.Client('',10000)
        #c.start()

    def setName(self, username, window):
        self.username = username
        self.initUI()
        window.destroy()
    
    def declarePortNum(self):
        self.writeOutput("ChatApp is waiting on port: " + str(self.port)) 

    def uclient_init(self):
        self.findInstance = client.udpClient()
        self.findInstance.start()
        self.writeOutput("Looking for existing instances.....please wait")

    def isLocalInstance(self, port):
        (addr, cport, success) = self.findInstance.search
        if success:
            self.writeOutput("Found existing instance at: " + addr +':'+cport)
            # import the existing graph structure
            self.dconnect(addr, int(cport))
        else:
            self.writeOutput("No existing instance found!") 
            self.writeOutput("Starting broadcast for this instance...")
            self.findInstance = None
            print "STARTING" +str(port)
            self.broadcast = server.udpServer(port)
            self.broadcast.start()

    # this does not work inside the connect function, perhaps connecting takes
    # too long.
    def retrieveGraph(self):
        if self.dc:
            self.dc.sock.send('retrievelegbat')
        else:
            self.network = graph.NetGraph(self,{self.node: []}, [(self.node, self.node, 0)] )
        self.writeOutput("Thanks for your patience - Your ChatApp is read to use!")
        self.writeOutput("...Remember to disconnect properly!")

    # for actual connections    
    def app_connect(self):
             
        addr_lst = []
        port_lst = []

        for node in self.network.nodes:
            print node+"HOW MANY NODES ARE THER???"
            addr_lst.append(node.split('::')[0])
            port_lst.append(int(node.split('::')[1]))
        ########################
        # save a spot for transmit new graph node message
        #
        #############################
        print "DID THIS FUCKING WORK"
        if self.dc:
            print "YES IT DID!"
            serv = client.Client(self, addr_lst, port_lst)
            serv.start()
            self.client = serv
        else:
            print "u dumbfuk"


    def exitApp(self):
        self.broadcast.isOn = 0
        self.server.isOn = 0
        del self.chatText
        del self.findInstance
        del self.broadcast
        del self.server
        del self.client
        del self.network
        sys.exit(1)
        os._exit(1)
        self.parent.destroy()

    def userver_init(self, window):
        serv = server.udpServer()
        serv.start()
        print self.server.port
        window.destroy()

        
   
    def nothing(self):
        print "nothing"

    def server_init(self, addr, port, window):
        serv = server.Server(self, addr)
        serv.start()
        self.server = serv
        if window:
            window.destroy()

    def dconnect(self, addr, port):
        if self.dc is None:
            serv = client.dClient(self, addr, port)
            serv.start()
            self.dc = serv
        else:
            self.writeOutput("GG")

 
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
        self.writeOutput("<you> : " + text)
        if self.client:
            self.client.sendMsg(text)
        if self.server:
            print "why so serious"
            self.server.send_through_server(text)


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
    root.geometry("1200x700+300+300")
    app = NetAppGUI(root)
    root.mainloop()
    def test():
        print "successful exit"
    atexit.register(test)

if __name__ == '__main__':
    main()
   
