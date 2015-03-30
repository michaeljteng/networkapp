try:
    import matplotlib.pyplot as plt
except:
    raise

import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import networkx as nx
from Tkinter import *
from heapq import *

maxint = 100000000000

class NetGraph(Frame):

    def __init__(self, parent, nodes, edges):
        Frame.__init__(self, parent, relief=RAISED, borderwidth=1)
        self.parent = parent
        self.nodes = nodes
        self.edges = edges
        self.G = nx.Graph()
        self.path = []
        self.found = None 
        self.graphFrame = Frame(self)
        self.initNetGraph()
        self.exButton = None
       

    def initNetGraph(self):    
        label = Label(self, text="Network Visualization") 
        label.pack()
        
        buttonsFrame = Frame(self)
        listButton = Button(buttonsFrame, text="List All Users", command=lambda: self.listUsers())
        mstButton = Button(buttonsFrame, text="MST", command=lambda: self.drawGraph(1))
        spButton = Button(buttonsFrame, text="Shortest Path", command=lambda: self.pathPrompt(self.parent))
        findButton = Button(buttonsFrame, text="Find User", command=lambda: self.findUser(self.parent))
        ogButton = Button(buttonsFrame, text="Original Graph", command=lambda: self.drawGraph(0))
        
        listButton.grid(row=0, column=5)
        mstButton.grid(row=0, column=1)
        spButton.grid(row=0, column=2)
        findButton.grid(row=0, column=3)
        ogButton.grid(row=0, column=4)
        buttonsFrame.pack()

        #initial graph is just one node always 
        for (x,y,w) in self.edges:
            self.G.add_edge(x,y)

        for node in self.nodes:
            self.G.add_node(node)

        self.graphFrame.pack()
        self.pack()
    
    # this is where graph gets created via the messages from instances indicating connection
    def new_connection(self, edge):
        node1 = edge[0]
        node2 = edge[1]
        weight = edge[2]
        if node1 not in self.nodes:
            self.nodes[node1] = []
        if node2 not in self.nodes:
            self.nodes[node2] = []
        if node1 not in self.G.nodes():
            self.G.add_node(node1)
        if node2 not in self.G.nodes():
            self.G.add_node(node2)
        if (node1, node2) not in self.G.edges():
            self.G.add_edge(node1, node2)
            
        self.edges.append(edge)
        self.nodes[node1].append((node2, weight))
        self.nodes[node2].append((node1, weight))
   
    # deletes local netowrk graphs node, then passes on message for other instances to follow suit
    def lost_connection(self, node):
        if self.nodes[node]:
            for (endpoint, weight) in self.nodes[node]:
                edge1 = (node, endpoint, weight)
                edge2 = (endpoint, node, weight)
                if edge1 in self.edges:
                    self.edges.remove(edge1)
                    self.G.remove_edge(node, endpoint)
                if edge2 in self.edges:
                    self.edges.remove(edge2)
                    self.G.remove_edge(endpoint, node)
                self.nodes[endpoint].remove((node, weight))
            if node in self.nodes:
                del self.nodes[node]
            if node in self.G.nodes():
                self.G.remove_node(node)
    
    # matplotlib figure into tkinter with networkx
    def drawGraph(self, flag):
        f = Figure(figsize=(5.5,6), dpi=100)
        a = f.add_subplot(111)       
        
        self.graphFrame.destroy()
        self.graphFrame = Frame(self)
        self.graphFrame.pack()
        
        canvas = FigureCanvasTkAgg(f, self.graphFrame)
        
        # nodes
        pos=nx.spring_layout(self.G)
        nx.draw(self.G, pos, with_labels=False, node_size=0, ax=a) 

        # edges
        if flag == 1:
            mstEdges = self.computeMST()
            nx.draw_networkx_edges(self.G,pos, edgelist=mstEdges, edge_color='b', style='dashed', width=5,ax=a)
        elif flag == 2:
            nx.draw_networkx_edges(self.G, pos, edgelist=self.path, edge_color='g', style='dashed', width=5, ax=a)
        elif flag == 3:
            if self.found:
                nx.draw_networkx_nodes(self.G, pos, nodelist=self.found, node_color='y', node_size=400, ax=a)
        nx.draw_networkx_edges(self.G,pos, width=1,ax=a)

        # labels
        nx.draw_networkx_labels(self.G,pos,font_size=6,font_family='sans-serif', ax=a)
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self.graphFrame)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)
#-------------------------------------------------------------------------------------#
# this is a minimum spanning tree algorithm using kruskal's algorithm, it has an      #
# advantage over prim's due to its ability to find the mst even if the graph has      #
# disconnected components - runs in O(Edges*Nodes*2), this is fine for our purposes   #
#-------------------------------------------------------------------------------------#
    def computeMST(self):
        
        kruskalEdges = sorted(self.edges, key=lambda (u,v,d): d)
        mstEdges = []

        # a forest of individual trees (one node each to start)
        kruskalForest = [set([node]) for node in self.nodes]
        
        # for each edge, starting with the smallest, we have 
        for (u,v,d) in kruskalEdges:
            ta = self.findInForest(u, kruskalForest)
            tb = self.findInForest(v, kruskalForest)
            # if they are in disjoint trees, then join them
            if ta != tb:
                mstEdges.append((u,v,d))
                tc = ta.union(tb)
                #create the new tree
                kruskalForest.remove(tb)
                kruskalForest.remove(ta)
                kruskalForest.append(tc)
        return mstEdges

    # helper function for computeMST, identifies if an edge is in the same forest or not
    # this is O(N) where N is the number of nodes
    def findInForest(self, item, lst):
        try:
            for s in lst:
                if item in s:
                    return s
        except:
            raise
#-----------------------------------------------------------------------------------#
# Shortest path algorithm using djikstra's algorithm along with a suspect           #
# decrease_key implementation                                                       #
#-----------------------------------------------------------------------------------#

    def djikstra(self, start, end, window):
        if start == end:
            self.parent.writeOutput("Same node!")
            self.path = []
            self.drawGraph(2)
            window.destroy()

        elif start not in self.nodes or end not in self.nodes:
            self.parent.writeOutput("Nodes not in graph!")
            self.path = []
            self.drawGraph(2)
            window.destroy()

        else:
            minheap = []
            dist = {}
            prev = {}
            # initialize the shits
            for node in self.nodes:
                if node == start:
                    dist[node] = (0, 1, node)
                    minheap.append((0, 1, node))
                else:
                    dist[node] = (maxint, 0, node)
                    minheap.append((maxint, 0, node))
                    prev[node] = 'undefined'
            heapify(minheap)
            
            # always visit the easiest possible, until heap is empty
            while minheap:
                (distance, visited, node) = heappop(minheap)
                dist[node] = (distance, 1, node)
                for (neighbor, distance_to) in self.nodes[node]:
                    if dist[neighbor][1] == 0:
                        alt = distance + distance_to
                        if alt < dist[neighbor][0]:
                            # makeshift decrease_key
                            minheap.remove(dist[neighbor])
                            dist[neighbor] = (alt, 0, neighbor)
                            # there is a way to reach the next node that is easier
                            prev[neighbor] = node
                            heappush(minheap, dist[neighbor])
            
            # path is found, compute it and return
            source = end
            result = []
            if prev[end] == 'undefined':
                self.parent.writeOutput("Path does not exist!")
            else:
                while source != start:
                    result.append((prev[source],source))
                    source = prev[source]
            self.path = result
            self.parent.writeOutput(str(result))
            self.drawGraph(2)
            window.destroy()
        window.destroy()
    
    # lists all users in the main chat
    def listUsers(self):
        self.parent.writeOutput(str(self.G.nodes()))
    
    # function called by findUser
    def returnUser(self, node, window):
        if node in self.nodes:
            self.found = node
            window.destroy()
        else:
            self.parent.writeOutput("User does not exist!")
            self.found = None
            window.destroy()
        # color the found node if it has been found
        self.drawGraph(3)

    # prompter for user find
    def findUser(self, master):
        top = Toplevel(master)
        top.title("user?")
        top.grab_set()
        Label(top, text="wtf").grid(row=0)
        port = Entry(top)
        port.grid(row=0, column=1)
        go = Button(top, text="launch", command=lambda: self.returnUser(port.get(), top))
        go.grid(row=2, column=1)

    # prompter for djikstra
    def pathPrompt(self, master):
        top = Toplevel(master)
        top.title("shortest path")
        top.grab_set()
        Label(top, text="Start:").grid(row=0)
        port1 = Entry(top)
        port1.grid(row=0, column=1)
        port1.focus_set()
        Label(top, text="End:").grid(row=1)
        port2 = Entry(top)
        port2.grid(row=1, column=1)
        port2.focus_set()
        go = Button(top, text="Launch", command=lambda: self.djikstra(port1.get(), port2.get(), top))
        go.grid(row=2, column=1)
        
