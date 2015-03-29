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
        self.search = ('','',0)

    def run(self):
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
                        print "got service announcement from", data[len('legbat'):]
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
        self.parent = parent # this is the tkinter widget
        self.addrs = addr_lst
        self.ports = port_lst
        self.socks = []
    
    def run(self):
        print len(self.addrs), "LENGTH OF ADDR LST:"
        for i in xrange(len(self.addrs)):
            server_address = (self.addrs[i], self.ports[i])
            # Create a TCP/IP socket
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socks.append(s)

            # Connect the socket to the port where the server is listening
            self.parent.writeOutput('Connecting to %s port %s' % server_address)
            
            s.connect(server_address)
            #self.parent.network.new_connection(str(s.getsockname()), (str(s.getsockname()),str(server_address), 0.5) )

        while 1:
            r,w,x = select.select(self.socks, self.socks, [])
            for s in r:
                try:
                    data = s.recv(1024)
                    print data
                    if data.startswith('legbat'):
                        jar = data[len('legbat'):]
                        pickles = jar.split('legbat')
                        p1 = pickle.loads(pickles[0])
                        p2 = pickle.loads(pickles[1])
                        print p1, p2
                        self.parent.network = graph.NetGraph(self.parent, p1, p2)

                    else:
                        self.parent.writeOutput("<"+str(s.getpeername())+"> : "+data)
                except:
                    print "u fucking scrub"
        
    def sendMsg(self, message):
        for s in self.socks:
            s.send(message)
        
        # for message in messages:

                # Send messages on both sockets
             #   for s in socks:
               #     print >>sys.stderr, '%s: sending "%s"' % (s.getsockname(), message)
               #     print "im sending", message
                #    s.send(message)

                # Read responses on both sockets
            #    for s in socks:
               #     data = s.recv(1024)
             #       if data:
                 #       print >>sys.stderr, '%s: received "%s"' % (s.getsockname(), data)
                 #   else:
                   #     print 'closing sasdf'
                      #  s.close()


