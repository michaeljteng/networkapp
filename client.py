import socket
import sys
import threading
import select
import Queue

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
                    print "your done"
                    serv.close()
                    print "u are truly done"
        except:
            print "this didnt do shit"
            print "wtf"
            
        self.search = (ap[0], ap[1], success)

#----------------------------------------------------------------#
# This is the main client class:                                 #
# It is multithreaded and uses select to wait on sockets in      #
# order to achieve asynchronous I/O                              #
#----------------------------------------------------------------#
class Client(threading.Thread):
    def __init__(self, parent, addr, port):
        threading.Thread.__init__(self)
        self.parent = parent # this is the tkinter widget
        self.addr = addr
        self.port = port
        self.socks = []
    
    def run(self):
        server_address = (self.addr, self.port)

        # Create a TCP/IP socket
        self.socks = [ socket.socket(socket.AF_INET, socket.SOCK_STREAM)]

        # Connect the socket to the port where the server is listening
        self.parent.writeOutput('Connecting to %s port %s' % server_address)
        for s in self.socks:
            s.connect(server_address)
        
        while 1:
            r,w,x = select.select(self.socks, self.socks, [])
            for s in r:
                try:
                    data = s.recv(1024)
                    self.parent.writeOutput("<"+str(s.getpeername()[0])+"> : "+data)
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


