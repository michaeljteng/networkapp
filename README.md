
This is a networked chat app with a graph gui.

-----------------------------------------------------------------------------------

This uses python and includes the tkinter module for the gui, with networkx. 
Use 'pip install $module'. 
Then, simply run 'python netapp.py' from a console. 
This app works as multiple instances on the same machine, as well as different
machines on the same local subnet. 

------------------------------------------------------------------------------------

The graph algorithms used are djikstra's for shortest path and kruskal's for mst. 
The time complexities are explained in the code comments. 

------------------------------------------------------------------------------------

If one node disconnects from the network, it will trigger the a safe close, 
while stops all the threads, close the sockets, as well as propagate a 
message to all the remaining nodes that it is no longer running and should be 
deleted from the graph

-----------------------------------------------------------------------------------
