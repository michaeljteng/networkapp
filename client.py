import socket
import sys
import threading
import select
import Queue

class Client(threading.Thread):
    def __init__(self, addr, port):
        threading.Thread.__init__(self)
        self.addr = addr
        self.port = port
    
    def run(self):
        server_address = ('', 50000)

        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print >>sys.stderr, 'connection to port'

        sock1.connect(server_address)
        sock2.connect(server_address)

        sock1.send('test1')
        sock2.send('test2')

        data1 = sock1.recv(1024)
        data2 = sock2.recv(1024)

        sock1.close()
        sock2.close()

class udpClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create UDP socket
        s_addr = ('', 50000)
        
        serv.settimeout(6)
        serv.bind(s_addr)
        aha = ''
        try:
            while 1:
                try:
                    
                    data, addr = serv.recvfrom(1024) #wait for a packet
                    if data.startswith('legbat'):
                        print "got service announcement from", data[len('legbat'):]
                        aha = data[len('legbat'):]
                        serv.close()
                except socket.timeout:
                    print "your done"
                    serv.close()
                    print "u are truly done"
        except:
            print "this didnt do shit"
            print "wtf"


