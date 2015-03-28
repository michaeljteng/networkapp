import socket
import sys
import threading
import select
import Queue

class Client(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent # this is the tkinter widget
        self.socks = []
    
    def run(self):
        server_address = ('localhost', 10000)

        # Create a TCP/IP socket
        self.socks = [ socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                  socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                  ]

        # Connect the socket to the port where the server is listening
        self.parent.writeOutput('connecting to %s port %s' % server_address)
        for s in self.socks:
            s.connect(server_address)
        
        while 1:
            r,w,x = select.select(self.socks, self.socks, [])
            for s in r:
                try:
                    data = s.recv(1024)
                    self.parent.writeOutput(data)
                except:
                    print "ASDFASDFASDFASDGAGWEG"
                    
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

class udpClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.search = ('',0)

    def run(self):
        serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create UDP socket
        s_addr = ('', 50000)
        
        serv.settimeout(6)
        serv.bind(s_addr)
        aha = ''
        success = 0
        try:
            while 1:
                try:
                    
                    data, addr = serv.recvfrom(1024) #wait for a packet
                    if data.startswith('legbat'):
                        print "got service announcement from", data[len('legbat'):]
                        aha = data[len('legbat'):]
                        success = 1
                        serv.close()
                except socket.timeout:
                    print "your done"
                    serv.close()
                    print "u are truly done"
        except:
            print "this didnt do shit"
            print "wtf"
            
        self.search = (aha, success)
