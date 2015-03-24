import socket
import sys
import threading
import select
import Queue
from time import sleep

class udpServer(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_addr = ('', 50000)

        serv.bind(s_addr)
        serv.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        my_ip = socket.gethostbyname(socket.gethostname())
        while 1:
            data = "legbat"+my_ip
            serv.sendto(data, ('<broadcast>', self.port))
            print "sent service announcement!" 
            sleep(5)

class Server(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    # select function polls sockets to avoid waiting on blocking procedures
    def relay_message(self, s, msg):
	    for sock in input_socks:
		    # if the socket is not the master server socket and
		    # if the socket is not s (i.e. the one sending the msg)
		    if sock != serv and sock != s:
			    try: 
				    sock.send(msg)
			    except: 
				    sock.close()
                    # bitchass closed from other end, this is where
                    # we add the shit to remove it from the graph and update
                    # fuck cs2
				    input_socks.remove(sock)

    def run(self):
        
        #create a TCP/IP socket
        try:
	        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	        serv.setblocking(0)
        except socket.error, msg:
	        print("failed to create socket")
	        sys.exit()

        # the '' thing is to list all possible hosts
        s_addr = ('', 10000)
        serv.bind(s_addr)

        # listens with a backlog of 5 connections
        serv.listen(5)


        # SELECT SHIT ########################################################

        # arguments to select are 3 lists containing communication channels to monitor
        # first -> list of objects to be checked for inc data to be read
        # second -> objects that receive outgoing data when there is room in their buffer
        # thid -> objects that may have i/o error

        # set up lists containing input sources and output destinations to be passed to select

        # socks which we expect to read from
        input_socks = [ serv ] 

        # socks which we expect to write to
        output_socks = []

        # the queues associated with the client sockets which acts as a buffer
        # in case the socket is not yet writable
        # {socket:Queue}
        msg_queue = {}

        while input_socks:
            print >>sys.stderr, '\nwaiting for next event'
            readable, writable, exceptional = select.select(input_socks, output_socks, input_socks)
            for s in readable:
                if s is serv:
                    # handle a new incoming connection
                    connection, client_address = s.accept()
                    print >>sys.stderr, 'new connection from', client_address
                    # the returned connection is a different port/socket
                    connection.setblocking(0)
                    self.relay_message(connection, "wtf is going on ")
                    # since new socket, put that shit into the input array
                    input_socks.append(connection)
                    
                    msg_queue[connection] = Queue.Queue()
                # if its not the master server, then it is a client waiting to be read
                else:
                    data = s.recv(1024)
                    if data:
                        print >>sys.stderr, 'recieved "%s" from "%s"' % (data, s.getpeername()) 
                        msg_queue[s].put(data)
                        
                        if s not in output_socks:
                            output_socks.append(s)
                    #if no readable data, then client has disconnected
                    else:
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        
                        # remove msg queue
                        del msg_queue[s]
            
            for s in writable:
                try:
                    next_msg = msg_queue[s].get_nowait()
                except Queue.Empty:
                    output_socks.remove(s)
                else:
                    print >>sys.stderr, 'sending'
                    s.send(next_msg)

            for s in exceptional:
                print >>sys.stderr, 'handling exceptional condition'
                input_socks.remove(s)
                if s in output_socks:
                    output_socks.remove(s)
                s.close()

                del msg_queue[s]
