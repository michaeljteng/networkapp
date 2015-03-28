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

        while 1:
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
