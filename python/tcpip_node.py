DEFAULT_MAX_NODES = 5
PRINTMAP_INDENT = 4

# This error is raised when all possible IP addresses have been used up.
class AddressSpaceFullError(Exception):
    pass

class TcpIpNode(object):
    """Represents a node on a network"""
    
    # Double-underscore methods (such as the next three) are special methods
    # which are called invisibly during certain situations. For example, __init__
    # is called when you create a new instance of a class. Here, we're just doing
    # some standard setup stuff, like storing the arguments as internal variables.
    def __init__(self, name, max_nodes=None):
        self.name = name
        self.maskLength = 0
        self._max_nodes = max_nodes
        self.nodes = []
        self.nameserver_clients = []
        self.nextAddress = 11

    # __str__ defines how this object should be represented as a string. For
    # example, when you print an instance.
    def __str__(self):
        if self.is_nameserver():
            ns = ""
        elif hasattr(self, 'nameserver'): 
            ns = "(NS: %s)" % self.nameserver.name
        else:
            ns = "(NO NAMESERVER)"
        return "%s %s (%s) %s" % (self.address, self.name, self.role(), ns)

    # __repr__ defines how this object is shown in interactive Python.
    def __repr__(self):
        return "<TcpIpNode name=%s, address=%s>" % (self.name, self.address)

    # Adds a node to this node's subnet. If the subnet is full, takes care of 
    # finding a subnet where the node can be attached.
    def add_node(self, node):
        node.maskLength += 1
        if not self._full():
            node.parent = self
            node.address = self._generate_address()
            self.nodes.append(node)
        else:
            subnet = (
                self._get_smallest_partially_filled_subnet() or
                self._get_empty_subnet() or 
                self._get_recursively_smallest_subnet()
            )
            subnet.add_node(node)

    # Sometimes a simulation has a fixed number of nodes per subnet, other times
    # you might want a fancier rule (like 8 nodes in the central network, then 
    # four nodes in the outer networks... When a node is created, max_nodes can
    # be either an integer or a function--if it's a function, this node will be
    # passed in as the argument. 
    def max_nodes(self):
        if isinstance(self._max_nodes, int):
            return self._max_nodes
        elif callable(self._max_nodes):
            return self._max_nodes(self)
        else:
            return DEFAULT_MAX_NODES
        
    # Returns a string describing this node's role.
    def role(self):
        if any(self.nodes):
            return "GATEWAY"
        elif any(self.nameserver_clients):
            return  "NAMESERVER SERVING %s" % ', '.join(["%s (%s)" % (c.name, c.address) for c in self.nameserver_clients])
        else:
            return  "NODE"

    # A recursive method used to print the network tree
    def print_tree(self, indent=0):
        print( '%s%s' % (' ' * indent, self))
        childIndent = indent + PRINTMAP_INDENT
        for child in self._get_nodes(recursive=False):
            child.print_tree(indent + PRINTMAP_INDENT)

    # Gets all the nodes in this node's subnet. If recursive is True, gets all
    # descendents of this node.
    def _get_nodes(self, recursive=False):
        nodes = self.nodes[:]
        if recursive:
            for gateway in self.nodes:
                nodes += gateway._get_nodes(recursive=True)
        return nodes

    # Returns a list of all nodes within a certain number of hops.
    # Let a hop be defined as moving to another node on the same network
    # With zero hops, we should only include ourselves. 
    # With one hop, we include parent, siblings, and children
    def _get_nodes_within_hops(self, hops):
        node_set = []
        leaves = [[self, hops]]
        while any(leaves):
            node, hops_left = leaves.pop(0)
            if not node in node_set:
                node_set.append(node)
            if hops_left > 0:
                adjacent_nodes = node.siblings() + node.nodes
                if hasattr(node, 'parent'):
                    adjacent_nodes.insert(0, node.parent)
                for adjacent_node in adjacent_nodes:
                    if not adjacent_node in node_set:
                        leaves.append([adjacent_node, hops_left - 1])
        return node_set
                    
    # Generates a new IP address for a node on the subnet. This is used when
    # adding a node.
    def _generate_address(self):
        addrParts = self.address.split('.')
        try:
            addrParts[self.maskLength] = str(self.nextAddress)
        except IndexError:
            raise AddressSpaceFullError("The address space is full. Increase max_nodes or ip_address_length")
        address = '.'.join(addrParts)
        self.nextAddress += 1
        return address

    # Check to see whether the subnet is full
    def _full(self):
        return len(self.nodes) >= self.max_nodes()

    # Returns all of this node's siblings, including itself
    def siblings(self):
        if not hasattr(self, 'parent'):
            return []
        return self.parent.nodes

    # Check to see whether this node is a gateway router
    def is_gateway(self):
        return any(self.nodes)

    # Check to see whether this node is a nameserver
    def is_nameserver(self):
        return any(self.nameserver_clients)

    # Returns the name of this node's network
    def get_network_name(self):
        network_name = '.'.join([loc for loc in self.parent.address.split('.') if loc != '10'])
        return network_name or "0"

    # Returns the name of the subnet (only makes sense if this is a gateway router
    def get_subnet_name(self):
        if not self.is_gateway():
            return "NO SUBNET"
        else:
            return self.nodes[0].get_network_name()

    # Finds a node with a partially-filled subnet. This and the following two 
    # methods are used to decide where to add a node if there's no room on the
    # immediate subnet.
    def _get_smallest_partially_filled_subnet(self):
        partially_full = [node for node in self.nodes if any(node.nodes) and 
                not node._full()]
        if not any(partially_full):
            return None
        smallest = partially_full[0]
        for child in partially_full:
            if any(child.nodes) and len(child._get_nodes()) < len(smallest._get_nodes()):
                smallest = child
        return smallest

    # Finds a node on the subnet which has no nodes of its own, if there is one
    def _get_empty_subnet(self):
        for child in self.nodes:
            if not any(child.nodes):
                return child

    # Finds the node on the subnet with the smallest subnet of its own
    def _get_recursively_smallest_subnet(self):
        if not any(self.nodes):
            return None
        def smaller(node_one, node_two):
            if len(node_one._get_nodes(True)) <= len(node_two._get_nodes(True)):
                return node_one
            else:
                return node_two
        return reduce(smaller, self.nodes, self.nodes[0])
