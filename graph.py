try:
    import matplotlib.pyplot as plt
except:
    raise

import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import networkx as nx
from Tkinter import *
import heapq

maxint = 100000000000

class NetGraph(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent, relief=RAISED, borderwidth=1)
        self.parent = parent
        self.nodes = {'a': [],'b': [],'c': [],'d': [],'e': [],'f': []}
        self.edges = [('a','f',0.4), ('b','e',0.4), ('e','d',0.7), ('a','c',0.2), ('c','d',0.4), ('a','d',0.7)]
        self.G = nx.Graph()
        # set up the matplotlib figure
        self.exists = 0
        self.graphFrame = Frame(self)
        self.initNetGraph()
        

    def initNetGraph(self):    
        label = Label(self, text="Network Visualization") 
        label.pack()
        
        buttonsFrame = Frame(self)
        mstButton = Button(buttonsFrame, text="MST", command=lambda: self.drawGraph(1))
        spButton = Button(buttonsFrame, text="Shortest Path", command=lambda: self.drawGraph(2))
        dfsButton = Button(buttonsFrame, text="Find User", command=lambda: self.drawGraph(3))
        ogButton = Button(buttonsFrame, text="Original Graph", command=lambda: self.drawGraph(0))
        
        mstButton.grid(row=0, column=1)
        spButton.grid(row=0, column=2)
        ogButton.grid(row=0, column=3)
        buttonsFrame.pack()

        # add nodes with visited property to 0 for Djikstra's and DFS
        for (x,y,w) in self.edges:
            self.G.add_edge(x,y,weight=w)
            self.nodes[x].append((y,w))
            self.nodes[y].append((x,w))
        for node in self.nodes:
            self.G.add_node(node,visited=0, distanceto=maxint, adjlist=self.nodes[node])

        self.graphFrame.pack()
        self.pack()
        
    def drawGraph(self, flag):
        f = Figure(figsize=(5,5), dpi=100)

        a = f.add_subplot(111)       

        if flag == 1:
            mstEdges = self.computeMST()

        pos=nx.spring_layout(self.G)
        
        if self.exists:
            self.graphFrame.destroy()
            self.graphFrame = Frame(self)
            self.graphFrame.pack()
            
        canvas = FigureCanvasTkAgg(f, self.graphFrame)
        
        # nodes
        nx.draw_networkx_nodes(self.G,pos,node_size=300, ax=a)

        # edges
        if flag == 1:
            nx.draw_networkx_edges(self.G,pos, edgelist=mstEdges, edge_color='b', style='dashed', width=5,ax=a)
        nx.draw_networkx_edges(self.G,pos, width=1,ax=a)


        # labels
        nx.draw_networkx_labels(self.G,pos,font_size=10,font_family='sans-serif', ax=a)

        #self.canvas.show()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self.graphFrame)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)


        self.exists = 1

    def computeMST(self):
        kruskalEdges = sorted(self.G.edges(data=True), key=lambda (u,v,d): d['weight'])
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
        print self.G.nodes(data=True)
        return mstEdges

    def findInForest(self, item, lst):
        try:
            for s in lst:
                if item in s:
                    return s
        except:
            raise

    def djikstra(self, start, end):
        # initialize the shits
        for (node, d) in self.G.nodes(data=True):
            if node == start:
                d['distanceto'] = 0
                d['visited'] = 1
            else:
                d['visited'] = 0 
                d['distanceto'] = maxint

        
