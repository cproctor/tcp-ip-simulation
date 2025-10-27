import networkx as nx
from itertools import pairwise
import matplotlib.pyplot as plt

class TcpIpSimulationGraph:
    def __init__(self, sim):
        "Expects a TcpIpSimulation"
        self.sim = sim
    
    def generate(self, size=8, outfile=None):
        G = nx.Graph()
        self.add_network(G, self.sim.rootNode, with_gateway=False)
        plt.figure(figsize=(size, size))
        nx.draw_spring(
            G, 
            width=5,
            with_labels=True,
            node_size=2000,
            node_color="#1f78b444",
            edge_color="#00000044",
            font_size=10,
        )
        if outfile:
            plt.savefig(outfile)
        else:
            plt.show()
        return G

    def add_network(self, G, gateway, with_gateway=True):
        node_ring = gateway.nodes[:]
        if with_gateway: 
            node_ring.append(gateway)
        if len(node_ring) > 2:
            node_ring.append(node_ring[0])
        for a, b in pairwise(node_ring):
            G.add_edge(self.node_string(a), self.node_string(b))
        for node in gateway.nodes:
            if node.is_gateway():
                self.add_network(G, node)

    def node_string(self, node):
        return f"{node.name}\n({node.address})"




