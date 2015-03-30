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
        
        serv.settimeout(2)
        serv.bind(s_addr)
        ap = ['','']
        success = 0
        while self.isOn:
            try:
                
                data, addr = serv.recvfrom(1024) #wait for a packet

                # success!
                if data.startswith('legbat'):
                    ap = data[len('legbat'):].split("::")
                    success = 1
                    serv.close()
                    self.isOn = 0

            # if socket times out, we failed to hear the broadcast
            except socket.timeout:
                serv.close()
                self.isOn = 0

        # record results
        self.search = (ap[0], ap[1], success)
        

class dClient(threading.Thread):
    def __init__(self, parent, addr, port):
        threading.Thread.__init__(self)
        self.daemon = True
        self.parent = parent
        self.addr = addr 
        self.port = port
        self.retrieved = None
        self.sock = None
        self.isOn = 0

    def run(self):
        self.isOn = 1
        server_addr = (self.addr, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.parent.writeOutput('Retrieving graph structure from %s, %s' % server_addr)
        self.parent.propagationChannel.append((self.parent.username, self.sock.getsockname()))  
        self.sock.connect(server_addr)
        self.parent.writeOutput('using addr:'+str(self.sock.getsockname()))
        try:
            data = self.sock.recv(2048)
            jar = data[len('legbat'):]
            pickles = jar.split('legbat')
            p1 = pickle.loads(pickles[0])
            p2 = pickle.loads(pickles[1])
            self.retrieved = (p1,p2)
        except:
            "bad things have happened to the broadcaster" 
            self.sock.close()
            self.parent.parent.destroy()


#----------------------------------------------------------------#
# This is the main client class:                                 #
# It is multithreaded and uses select to wait on sockets in      #
# order to achieve asynchronous I/O                              #
#----------------------------------------------------------------#
class Client(threading.Thread):
    def __init__(self, parent, addr_lst, port_lst, edge_lst):
        threading.Thread.__init__(self)
        self.daemon = True
        self.isOn = 0
        self.parent = parent # this is the tkinter widget
        self.addrs = addr_lst
        self.ports = port_lst
        self.edges = edge_lst
        self.successes = 0
        self.socks = []
        self.message_queues = {}
        self.new_edges = []
        self.outputs = []
    
    def run(self):
        self.isOn = 1
        self.parent.network = graph.NetGraph(self.parent, {self.parent.node: []}, [])
        
        for edge in self.edges:
            self.parent.network.new_connection(edge)
        
        for i in xrange(len(self.addrs)):
            if self.successes == 4:
                break
            
            # first check the degree of attempted connections, may be equal to 8 already
            node2 = self.addrs[i]+'::'+str(self.ports[i])
            if node2 in self.parent.network.nodes:
                degree = len(self.parent.network.nodes[node2]) # the adj list for this node
                if degree >= 8:
                    break

            server_address = (self.addrs[i], self.ports[i])
            # Create a TCP/IP socket
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socks.append(s)
            self.message_queues[s] = Queue.Queue()
            # Connect the socket to the port where the server is listening
            self.parent.writeOutput('Connecting to %s port %s' % server_address)
            
            s.connect(server_address)
            node1 = self.parent.node
            
            edge = (node1, node2, 0.5)

            self.parent.network.new_connection(edge)
            new_edge = pickle.dumps(edge)
            self.new_edges.append(new_edge)
            self.parent.propagationChannel.append((self.parent.username, s.getsockname()))
            self.successes += 1

        for edge in self.new_edges:
            self.sendMsg('l3gb4t'+':aVZjW-:'+edge+':aVZjW-:')
        while self.isOn:
            r,w,x = select.select(self.socks, self.outputs, self.socks)
            
            for s in r:
                data = s.recv(1048576)
                if data.startswith('legbat'):
                    jar = data[len('legbat'):]
                    pickles = jar.split('legbat')
                    p1 = pickle.loads(pickles[0])
                    p2 = pickle.loads(pickles[1])
                
                elif data.startswith('l3gb4t'):
                    jar = data.split(':aVZjW-:')
                    p = pickle.loads(jar[1])
                    self.parent.network.new_connection(p)

                    p_prop = pickle.loads(jar[2])
                    p_new = pickle.dumps(p_prop + self.parent.propagationChannel)


                    self.message_queues[s].put('l3gb4t'+':aVZjW-:'+jar[1]+':aVZjW-:'+p_new)
                    if s not in self.outputs:
                        self.outputs.append(s)

                elif data:
                    jar = data.split(':F2Ua-0:')
                    p_prop = pickle.loads(jar[1])
                    p_new = pickle.dumps(p_prop + self.parent.propagationChannel)
                    self.parent.writeOutput("<"+p_prop[0][0]+">: "+jar[0])
                    
                    self.message_queues[s].put(jar[0]+':F2Ua-0:'+p_new)
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
                    if next_msg.startswith('l3gb4t'):
                        jar = next_msg.split(':aVZjW-:')
                        p_prop = pickle.loads(jar[2])
                        already_sent = 0
                        for (uname, sockname) in p_prop:
                            if s.getpeername() == sockname:
                                already_sent = 1
                        if not already_sent:
                            s.send(next_msg)
                    else:
                        jar = next_msg.split(':F2Ua-0:')
                        p_prop = pickle.loads(jar[1])
                        already_sent = 0
                        for (uname, sockname) in p_prop:
                            if s.getpeername() == sockname:
                                already_sent = 1
                        if not already_sent:
                            s.send(next_msg)


            for s in x:
                self.socks.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                del self.message_queues[s]

        for s in self.socks:
            s.close()
    
    # use this to identify msgs that are sent from this instance first
    def sendMsg(self, message):
        for s in self.socks:
            p = pickle.dumps(self.parent.propagationChannel)
            if message.startswith('l3gb4t'):
                s.send(message+p)
            else:
                s.send(message+':F2Ua-0:'+p)



