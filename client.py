import socket
import sys
import threading
import select
import Queue
import pickle
import graph

#----------------------------------------------------------------#
# This is the broadcast client, initialized to discover          #
# existing instances on the local subnet                         #
#----------------------------------------------------------------#
class udpClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.search = ('','',0)
        self.isOn = 0

    def run(self):
        self.isOn = 1
        serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create UDP socket
        # use all network interfaces, broadcast port always 
        # hardcoded to 50000 to avoid confusion
        s_addr = ('', 50000)
        
        serv.settimeout(6)
        serv.bind(s_addr)
        ap = ['','']
        success = 0
        try:
            while 1:
                try:
                    
                    data, addr = serv.recvfrom(1024) #wait for a packet
                    if data.startswith('legbat'):
                        #print "got service announcement from", data[len('legbat'):]
                        ap = data[len('legbat'):].split("::")
                        success = 1
                        serv.close()
                except socket.timeout:
                    serv.close()
        except:
            print "done searching"

        # record results
        self.search = (ap[0], ap[1], success)
        

class dClient(threading.Thread):
    def __init__(self, parent, addr, port):
        threading.Thread.__init__(self)
        self.daemon = True
        self.parent = parent
        self.addr = addr 
        self.port = port
        self.sock = None

    def run(self):
        server_addr = (self.addr, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.parent.writeOutput('Retrieving graph structure from %s, %s' % server_addr)
      
        self.sock.connect(server_addr)
        self.parent.writeOutput('using addr:'+str(self.sock.getsockname()))
        try:
            data = self.sock.recv(2048)
            print data
            if data.startswith('legbat'):
                jar = data[len('legbat'):]
                pickles = jar.split('legbat')
                p1 = pickle.loads(pickles[0])
                p2 = pickle.loads(pickles[1])
                print p1, p2
                self.parent.network = graph.NetGraph(self.parent, p1, p2)
            else:
                print "its dover"
        except:
            print "u scrub"
    


#----------------------------------------------------------------#
# This is the main client class:                                 #
# It is multithreaded and uses select to wait on sockets in      #
# order to achieve asynchronous I/O                              #
#----------------------------------------------------------------#
class Client(threading.Thread):
    def __init__(self, parent, addr_lst, port_lst):
        threading.Thread.__init__(self)
        self.daemon = True
        self.isOn = 0
        self.parent = parent # this is the tkinter widget
        self.addrs = addr_lst
        self.ports = port_lst
        self.socks = []
        self.message_queues = {}
        self.outputs = []
    
    def run(self):
        self.isOn = 1
        for i in xrange(len(self.addrs)):
            server_address = (self.addrs[i], self.ports[i])
            # Create a TCP/IP socket
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socks.append(s)
            self.message_queues[s] = Queue.Queue()
            # Connect the socket to the port where the server is listening
            self.parent.writeOutput('Connecting to %s port %s' % server_address)
            
            s.connect(server_address)
            node1 = self.parent.node
            node2 = self.addrs[i]+'::'+str(self.ports[i])
            edge = (node1, node2, 0.5)

            self.parent.network.new_connection(edge)
        
        while self.isOn:
            r,w,x = select.select(self.socks, self.outputs, self.socks)
            
            for s in r:
                data = s.recv(1024)
                if data.startswith('legbat'):
                    jar = data[len('legbat'):]
                    pickles = jar.split('legbat')
                    p1 = pickle.loads(pickles[0])
                    p2 = pickle.loads(pickles[1])
                    print p1, p2
                    self.parent.network = graph.NetGraph(self.parent, p1, p2)
                    break
                if data:
                    self.parent.writeOutput("<"+str(s.getpeername())+"> : "+data)
                    self.message_queues[s].put(data)
                    if s not in self.outputs:
                        self.outputs.append(s)
                else:
                    self.parent.writeOutput('closing')
                    if s in self.outputs:
                        self.outputs.remove(s)
                    self.socks.remove(s)
                    s.close()
                    del self.message_queues[s]
            for s in w:
                try:
                    next_msg = self.message_queues[s].get_nowait()
                except Queue.Empty:
                    self.outputs.remove(s)
                else:
                    s.send(next_msg+'echo')
                    print "holding"

            for s in x:
                self.socks.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                del self.message_queues[s]

        for s in self.socks:
            s.close()
        print "EXITED" 
        
    def sendMsg(self, message):
        for s in self.socks:
            s.send(message)
