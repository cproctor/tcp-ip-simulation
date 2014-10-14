from jinja2 import Environment, FileSystemLoader
from random import choice
from os.path import dirname, realpath, join
from tcpip_node import TcpIpNode, AddressSpaceFullError

class TcpIpSimulation(object):
    """Creates docmuentation for a TCP/IP simulation with any size 
    of students."""

    def __init__(self, participants, outfile="simulation.html",
            max_nodes=6,
            nodes_per_nameserver=6,
            ip_address_length=2):
        self.outfile = outfile
        self.nodes_per_nameserver = nodes_per_nameserver
        self.env = Environment(loader=FileSystemLoader(
                join(dirname(realpath(__file__)), "templates")))
        self.rootNode = TcpIpNode(self.env, 'ROOT', max_nodes=max_nodes)
        self.rootNode.address = '.'.join(["10"] * ip_address_length)
        for participant in participants:
            node = TcpIpNode(self.env, participant, max_nodes=max_nodes)
            self.rootNode.add_node(node)

        self.assign_nameservers()

        #all_nodes = self._get_depth_first_node_list()
        #all_nodes.pop()
        #for node in all_nodes:
            #print "%s (%s): %s (%s)" % (node.name, node.address, node.nameserver.name, node.nameserver.address)

        #self.update_nameserver_tables()
        #self.assign_partners()

    def print_tree(self):
        print("NETWORK TREE")
        self.rootNode.print_tree()
            
    def generate(self):
        template = self.env.get_template('simulation.jinja2')
        with open(self.outfile, 'w') as outfile:
            outfile.write(template.render(
                    {'nodes': self.rootNode.get_nodes(recursive=True)}))

    def _get_depth_first_node_list(self):
        node_list = []
        def depth_first_node_list(node):
            for child in node.nodes:
                depth_first_node_list(child)
            node_list.append(node)
        depth_first_node_list(self.rootNode)
        return node_list

    def _get_breadth_first_node_list(self):
        node_list = []
        def breadth_first_node_list(node):
            node_list.append(node)
            for child in node.nodes:
                breadth_first_node_list(child)
        breadth_first_node_list(self.rootNode)
        return node_list

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
    def assign_nameservers(self):
        node_list = self._get_breadth_first_node_list()
        # Don't want ROOT
        node_list.pop(0)

        hops = 0
        while len(node_list) >= self.nodes_per_nameserver:
            hops += 1
            #print("Assigning nameservers for clients within %s hops" % hops)
            while True:
                new_nameserver, clients = self._find_new_nameserver(node_list, hops)
                if new_nameserver is None:
                    break
                #print("Found %s clients for new nameserver %s" % (len(clients), new_nameserver.name))
                for client in clients:
                    node_list.remove(client)
                    self._assign_client_to_nameserver(client, new_nameserver)
        #print("FINISHED REGULAR ASSIGNMENT; LEFTOVERS: %s" % [node.name for node in node_list])

        # And finally, the remnants get assigned.
        if any(node_list):
            final_nameserver = node_list[-1]
            for client in node_list:
                self._assign_client_to_nameserver(client, final_nameserver)

    # Return the first node which has nodes_per_nameserver potential clients,
    # where a potential client is a node without a nameserver within hops hops
    def _find_new_nameserver(self, node_list, hops):
        for potential_nameserver in node_list:

            # Gateways are ineligible to be nameservers
            if potential_nameserver.is_gateway():
                continue
            nodes_in_range = potential_nameserver._get_nodes_within_hops(hops)
            potential_clients = filter(lambda n: not hasattr(n, 'nameserver') and n is not self.rootNode, nodes_in_range) 
            if len(potential_clients) >= self.nodes_per_nameserver:
                return [potential_nameserver, potential_clients[:self.nodes_per_nameserver]]
        return [None, None]
            
    def _assign_client_to_nameserver(self, client, nameserver):
        client.nameserver = nameserver
        nameserver.nameserver_clients.append(client)
        nameserver.simulation = self
