from jinja2 import Environment, FileSystemLoader
from random import choice
from os.path import dirname, realpath, join
from tcpip_node import TcpIpNode, AddressSpaceFullError

# This error is raised when it's impossible to assign a nameserver to all the
# nodes. This only happens in really weird cases--for example, when almost all 
# the nodes are gateway routers (try setting max_nodes to 1...).
class NameserverAssignmentError(Exception): 
    pass

# The TcpIpSimulation object is the only a user should need to interact
# with to set up a simulation.
class TcpIpSimulation(object):
    """Creates docmuentation for a TCP/IP simulation with any size 
    of students."""

    # The __init__ method is always called when a new instance of a class
    # is created. This sets up the simulation.
    def __init__(self, participants, outfile="simulation.html",
            max_nodes=6,
            nodes_per_nameserver=6,
            ip_address_length=3):
        self.outfile = outfile
        self.nodes_per_nameserver = nodes_per_nameserver
        self.env = Environment(loader=FileSystemLoader(
                join(dirname(realpath(__file__)), "templates")))
        self.rootNode = TcpIpNode('ROOT', max_nodes=max_nodes)
        self.rootNode.address = '.'.join(["10"] * ip_address_length)
        for participant in participants:
            node = TcpIpNode(participant, max_nodes=max_nodes)
            self.rootNode.add_node(node)

        self._assign_nameservers()

    # Prints out a network tree
    def print_tree(self):
        print("NETWORK TREE")
        self.rootNode.print_tree()

    # Prints out a directory
    def print_directory(self):
        print("DIRECTORY")
        directory = self._get_directory()
        for name in sorted(directory.keys()):
            print("%s: %s" % (name, directory[name]))
            
    # Creates a HTML file ready for printing, which contains all the 
    # instructions, one page for each participant
    def generate_instructions(self):
        template = self.env.get_template('simulation.jinja2')
        nodes = []
        for node in self.rootNode._get_nodes(recursive=True):
            nodes.append({
                "name": node.name,
                "address": node.address,
                "nameserver": node.nameserver.address,
                "network": node.get_network_name(),
                "subnet": node.get_subnet_name(),
                "is_nameserver": node.is_nameserver(),
                "is_gateway": node.is_gateway()
            })
        with open(self.outfile, 'w') as outfile:
            outfile.write(template.render(
                    {'nodes': nodes}))

    # Assembles a directory by going through all the nodes and getting their
    # names and addresses. Returns a dict mapping names to addresses.
    def _get_directory(self):
        directory = {}
        def add_to_directory(node):
            directory[node.name] = node.address
            for child in node.nodes:
                add_to_directory(child)
        add_to_directory(self.rootNode)
        return directory

    # Each node will have a nameserver who is provides IP address lookups.
    # Gateway Routers are ineligle to be nameservers. A nameserver may serve
    # any nodes accessible by upward or lateral traverses of the tree. So to
    # assign nameservers, start at the top of the tree, looking for a node which 
    # could serve as a nameserver. When one is found, pop off its potential
    # clients and assign them to one another. 
    # The rationale for requiring nameserver traffic to go downhill is that
    # the center of the network will become extremely busy, so we should route
    # these requests away when possible. 
    def _assign_nameservers(self):
        node_list = self._get_breadth_first_node_list()
        # Don't want ROOT
        node_list.pop(0)
        hops = 0
        # As long as there are enough nodes left to fill a nameserver, find
        # them and set up a new nameserver.
        while len(node_list) >= self.nodes_per_nameserver:
            hops += 1
            while True:
                new_nameserver, clients = self._find_new_nameserver(node_list, hops)
                if new_nameserver is None:
                    break
                for client in clients:
                    node_list.remove(client)
                    self._assign_client_to_nameserver(client, new_nameserver)
        # At the end, maybe there are a few nodes left. Create a new nameserver
        # and assign all the nodes to this nameserver.
        if any(node_list):
            final_nameserver = node_list[-1]
            if final_nameserver.is_gateway():
                raise NameserverAssignmentError("Cannot assign gateway %s as a nameserver." % final_nameserver)
            for client in node_list:
                self._assign_client_to_nameserver(client, final_nameserver)

    # Returns a list of all nodes, starting at the root, then progressing 
    # gradually outward
    def _get_breadth_first_node_list(self):
        node_list = []
        def breadth_first_node_list(node):
            node_list.append(node)
            for child in node.nodes:
                breadth_first_node_list(child)
        breadth_first_node_list(self.rootNode)
        return node_list

    # Return the first node which has nodes_per_nameserver potential clients,
    # where a potential client is a node without a nameserver within hops hops
    def _find_new_nameserver(self, node_list, hops):
        for potential_nameserver in node_list:
            # Gateways are ineligible to be nameservers
            if potential_nameserver.is_gateway():
                continue
            nodes_in_range = potential_nameserver._get_nodes_within_hops(hops)
            potential_clients = filter(lambda n: not hasattr(n, 'nameserver') 
                    and n is not self.rootNode, nodes_in_range) 
            if len(potential_clients) >= self.nodes_per_nameserver:
                return [potential_nameserver, potential_clients[:self.nodes_per_nameserver]]
        return [None, None]
            
    # To assign a client to a nameserver, tell the nameserver it ha a new client,
    # tell the nameserver how to reach this simulation (to get the directory), and 
    # tell the client who its nameserver is.
    def _assign_client_to_nameserver(self, client, nameserver):
        nameserver.nameserver_clients.append(client)
        nameserver.simulation = self
        client.nameserver = nameserver
