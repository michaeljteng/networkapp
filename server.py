import socket
import sys
import threading
import select
import Queue
from time import sleep

class udpServer(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = str(port)

    def run(self):
        serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_addr = ('', 0)
        print "WTFFFF" + self.port
        serv.bind(s_addr)
        serv.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            my_ip = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            print "wtf"
            my_ip = 'ur fucked'
        while 1:
            data = "legbat"+my_ip+"::"+self.port
            serv.sendto(data, ('<broadcast>', 50000))
            print "sent service announcement to ", data 
            sleep(5)

class Server(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        self.port = 0 #TBD
        self.message_queues = {}
        self.outputs = []

    def run(self):
        #create a TCP/IP socket
        try:
	        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	        server.setblocking(0)
        except socket.error, msg:
	        self.parent.writeOutput("failed to create socket")
	        sys.exit()

        # the '' thing is to list all possible hosts
        s_addr = (socket.gethostbyname(socket.gethostname()), 0)
        server.bind(s_addr)
        print self.parent.port
        self.parent.port = server.getsockname()[1]
        print self.parent.port
        # listens with a backlog of 5 connections
        server.listen(5)


        # Sockets from which we expect to read
        #inputs = [ server ]
        inputs = [ server ]
        # Sockets to which we expect to write
        outputs = [ ]
        
        while inputs:

            # Wait for at least one of the sockets to be ready for processing
            #self.parent.writeOutput('\nwaiting for the next event')
            readable, writable, exceptional = select.select(inputs, self.outputs, inputs)

            # Handle inputs
            for s in readable:

                if s is server:
                    print "WE GOT THIS FAR"
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = s.accept()
                    self.parent.writeOutput('new connection from' + str(client_address))
                    connection.setblocking(0)
                    inputs.append(connection)

                    # Give the connection a queue for data we want to send
                    self.message_queues[connection] = Queue.Queue()

                else:
                    data = s.recv(1024)
                    print data
                    if data:
                        # A readable client socket has data
                        self.parent.writeOutput("<"+str(s.getpeername()[0])+"> : "+data)
                        self.message_queues[s].put(data)
                        # Add output channel for response
                        if s not in outputs:
                            self.outputs.append(s)


                    else:
                        # Interpret empty result as closed connection
                        self.parent.writeOutput('closing' + str(client_address) + 'after reading no data')
                        # Stop listening for input on the connection
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()

                        # Remove message queue
                        del self.message_queues[s]

            # Handle outputs
            for s in writable:
                try:
                    next_msg = self.message_queues[s].get_nowait()
                except Queue.Empty:
                    # No messages waiting so stop checking for writability.
                    #self.parent.writeOutput('output queue for' + str(s.getpeername()) + 'is empty')
                    self.outputs.remove(s)
                else:
                    #self.parent.writeOutput('sending "%s" to %s' % (next_msg, s.getpeername()))
                    # REMBER THIS SETUP IT IS FOR PROPAGATION!!!!!
                    #s.send(next_msg)
                    print "holding"

            # Handle "exceptional conditions"
            for s in exceptional:
                self.parent.writeOutput('handling exceptional condition for' + str(s.getpeername()))
                # Stop listening for input on the connection
                inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)
                s.close()

                # Remove message queue
                del self.message_queues[s]
             
    def send_through_server(self, message):
        for s in self.message_queues:
            print "dont work"
            s.send(message)
            #self.message_queues[s].put(message)
                # Add output channel for response
            #if s not in self.outputs:
                #self.outputs.append(s)



 
