import socket
import sys
import threading
import select
import Queue
import pickle
from time import sleep

class udpServer(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.daemon = True
        self.port = str(port)
        self.isOn = 0

    def run(self):
        self.isOn = 1
        serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_addr = ('', 0)
        serv.bind(s_addr)
        serv.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            my_ip = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            print "wtf"
            my_ip = 'ur completely fucked'
        while self.isOn:
            data = "legbat"+my_ip+"::"+self.port
            serv.sendto(data, ('<broadcast>', 50000))
            #print "sent service announcement to ", data 
            sleep(0.1)
        serv.close()

class Server(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.daemon = True
        self.parent = parent
        self.port = 0 #TBD
        self.message_queues = {}
        self.outputs = []
        self.inputs = []
        self.isOn = 0

    def run(self):
        self.isOn = 1
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
        self.parent.node = str(server.getsockname()[0])+'::'+str(server.getsockname()[1])
        self.parent.port = server.getsockname()[1]
        # listens with a backlog of 5 connections
        server.listen(5)

        self.inputs.append(server)
        self.parent.propagationChannel.append((self.parent.username, server.getsockname())) 
        while self.isOn:

            # Wait for at least one of the sockets to be ready for processing
            r, w, x = select.select(self.inputs, self.outputs, self.inputs)

            # Handle inputs
            for s in r:

                if s is server:
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = s.accept()
                    self.parent.writeOutput('new connection from' + str(client_address))
                    connection.setblocking(0)
                    self.inputs.append(connection)

                    # Give the connection a queue for data we want to send
                    self.message_queues[connection] = Queue.Queue()

                else:
                    data = s.recv(1024)
                    if data.startswith('retrievelegbat'):
                        p1 = pickle.dumps(self.parent.network.nodes)
                        p2 = pickle.dumps(self.parent.network.edges)
                        self.send_through_server('legbat'+p1+'legbat'+p2)
                        break
                    if data.startswith('l3gb4t'):
                        jar = data.split(':aVZjW-:')
                        p = pickle.loads(jar[1])
                        self.parent.network.new_connection(p)
                        print "THE JAR"
                        print jar
                        p_prop = pickle.loads(jar[2])
                        p_new = pickle.dumps(p_prop + self.parent.propagationChannel)


                        self.message_queues[s].put('l3gb4t'+':aVZjW-:'+jar[1]+':aVZjW-:'+p_new)
                        if s not in self.outputs:
                            self.outputs.append(s)
                        break
                    if data:
                        jar = data.split(':F2Ua-0:')
                        p_prop = pickle.loads(jar[1])
                        p_new = pickle.dumps(p_prop + self.parent.propagationChannel)
                        # A readable client socket has data
                        self.parent.writeOutput("<"+p_prop[0][0]+">: "+jar[0])
                        
                        self.message_queues[s].put(jar[0]+':F2Ua-0:'+p_new)
                        # Add output channel for response
                        if s not in self.outputs:
                            self.outputs.append(s)


                    else:
                        # Interpret empty result as closed connection
                        self.parent.writeOutput('closing' + str(client_address) + 'after reading no data')
                        # Stop listening for input on the connection
                        if s in self.outputs:
                            self.outputs.remove(s)
                        self.inputs.remove(s)
                        s.close()

                        # Remove message queue
                        del self.message_queues[s]

            # Handle outputs
            for s in w:
                try:
                    next_msg = self.message_queues[s].get_nowait()
                except Queue.Empty:
                    # No messages waiting so stop checking for writability.
                    #self.parent.writeOutput('output queue for' + str(s.getpeername()) + 'is empty')
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


            # Handle "exceptional conditions"
            for s in x:
                self.parent.writeOutput('handling exceptional condition for' + str(s.getpeername()))
                # Stop listening for input on the connection
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()

                # Remove message queue
                del self.message_queues[s]
        server.close()   

    def send_through_server(self, message):
        for s in self.message_queues:
            p = pickle.dumps(self.parent.propagationChannel)
            s.send(message+':F2Ua-0:'+p)

         
