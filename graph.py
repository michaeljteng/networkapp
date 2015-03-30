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
        # set up the matplotlib figure
        self.path = []
        self.found = None 
        self.graphFrame = Frame(self)
        self.initNetGraph()
        self.exButton = None
        

    def initNetGraph(self):    
        label = Label(self, text="Network Visualization") 
        label.pack()
        
        buttonsFrame = Frame(self)
        mstButton = Button(buttonsFrame, text="MST", command=lambda: self.drawGraph(1))
        spButton = Button(buttonsFrame, text="Shortest Path", command=lambda: self.pathPrompt(self.parent))
        findButton = Button(buttonsFrame, text="Find User", command=lambda: self.findUser(self.parent))
        ogButton = Button(buttonsFrame, text="Original Graph", command=lambda: self.drawGraph(0))
        
        mstButton.grid(row=0, column=1)
        spButton.grid(row=0, column=2)
        findButton.grid(row=0, column=3)
        ogButton.grid(row=0, column=4)
        buttonsFrame.pack()

        # add nodes with visited property to 0 for Djikstra's and DFS
        
        for (x,y,w) in self.edges:
            self.G.add_edge(x,y)

         #   self.nodes[x].append((y,w))
          #  self.nodes[y].append((x,w))
        
        for node in self.nodes:
            self.G.add_node(node)

        self.graphFrame.pack()
        self.pack()

    def new_connection(self, edge):
        node1 = edge[0]
        node2 = edge[1]
        weight = edge[2]
        print self.nodes
        print self.edges
        print self.G.nodes()
        print self.G.edges()
        if node1 not in self.nodes:
            self.nodes[node1] = []
            print 1
        if node2 not in self.nodes:
            self.nodes[node2] = []
            print 2
        if node1 not in self.G.nodes():
            self.G.add_node(node1)
            print 3
        if node2 not in self.G.nodes():
            self.G.add_node(node2)
            print 4
        if (node1, node2) not in self.G.edges():
            self.G.add_edge(node1, node2)
            
        self.edges.append(edge)
        self.nodes[node1].append((node2, weight))
        self.nodes[node2].append((node1, weight))
        
    def drawGraph(self, flag):
        f = Figure(figsize=(6,5.5), dpi=100)

        a = f.add_subplot(111)       

        
        self.graphFrame.destroy()
        self.graphFrame = Frame(self)
        self.graphFrame.pack()
        
        canvas = FigureCanvasTkAgg(f, self.graphFrame)
        
        # nodes
        pos=nx.spring_layout(self.G)
        nx.draw_networkx_nodes(self.G,pos,node_size=300, ax=a)

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
        nx.draw_networkx_labels(self.G,pos,font_size=13,font_family='sans-serif', ax=a)

        #self.canvas.show()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self.graphFrame)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

    def computeMST(self):
        #kruskalEdges = sorted(self.G.edges(data=True), key=lambda (u,v,d): d['weight'])
        kruskalEdges = sorted(self.edges, key=lambda (u,v,d): d)
        mstEdges = []

        kruskalForest = [set([node]) for node in self.nodes]
        print kruskalForest
        
        for (u,v,d) in kruskalEdges:
            print u, v
            ta = self.findInForest(u, kruskalForest)
            tb = self.findInForest(v, kruskalForest)
            print ta,tb
            if ta != tb:
                mstEdges.append((u,v,d))
                tc = ta.union(tb)
                kruskalForest.remove(tb)
                kruskalForest.remove(ta)
                kruskalForest.append(tc)
            print kruskalForest
        return mstEdges

    def findInForest(self, item, lst):
        try:
            for s in lst:
                if item in s:
                    return s
        except:
            raise

    def djikstra(self, start, end, window):
        if start == end:
            print "nice query u pro"
            self.path = []
            self.drawGraph(2)
            window.destroy()

        elif start not in self.nodes or end not in self.nodes:
            print "your query is impossible"
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
            
            while minheap:
                (distance, visited, node) = heappop(minheap)
                dist[node] = (distance, 1, node)
                for (neighbor, distance_to) in self.nodes[node]:
                    if dist[neighbor][1] == 0:
                        alt = distance + distance_to
                        if alt < dist[neighbor][0]:
                            minheap.remove(dist[neighbor])
                            dist[neighbor] = (alt, 0, neighbor)
                            prev[neighbor] = node
                            heappush(minheap, dist[neighbor])
            
            # path is found, compute it and return
            source = end
            result = []
            if prev[end] == 'undefined':
                print "no path"
            else:
                while source != start:
                    result.append((prev[source],source))
                    source = prev[source]
            self.path = result
            print result 
            self.drawGraph(2)
            window.destroy()
        window.destroy()

    def themostuseless(self, node, window):
        if node in self.nodes:
            self.found = node
            window.destroy()
        else:
            print "not in graph"
            self.found = None
            window.destroy()

        self.drawGraph(3)

    def findUser(self, master):
        top = Toplevel(master)
        top.title("user?")
        top.grab_set()
        Label(top, text="wtf").grid(row=0)
        port = Entry(top)
        port.grid(row=0, column=1)
        go = Button(top, text="launch", command=lambda: self.themostuseless(port.get(), top))
        go.grid(row=2, column=1)

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
        go = Button(top, text="Launch", command=lambda: self.new_connection(port1.get(), port2.get(), top))
        go.grid(row=2, column=1)
        
