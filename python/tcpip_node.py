DEFAULT_MAX_NODES = 5
PRINTMAP_INDENT = 4

class AddressSpaceFullError(Exception):
    pass

class TcpIpNode(object):
    """Represents a node on a network"""
    
    isNameserver = False

    def __init__(self, env, name, max_nodes=None):
        self.env = env
        self.name = name
        self.maskLength = 0
        if isinstance(max_nodes, int):
            self.maxNodes = max_nodes
        elif callable(max_nodes):
            self.maxNodes = max_nodes(self)
        else:
            self.maxNodex = DEFAULT_MAX_NODES
        self.nodes = []
        self.nameserver_clients = []
        self.nextAddress = 11

    def __str__(self):
        if self.is_nameserver():
            ns = ""
        elif hasattr(self, 'nameserver'): 
            ns = "(NS: %s)" % self.nameserver.name
        else:
            ns = "(NO NAMESERVER)"
        return "%s %s (%s) %s" % (self.address, self.name, self.role(), ns)

    def __repr__(self):
        return "<TcpIpNode name=%s, address=%s>" % (self.name, self.address)

    def render_instructions(self):
        return self.env.get_template(self._template_file()).render(self.__dict__)

    def role(self):
        if any(self.nodes):
            return "GATEWAY"
        elif any(self.nameserver_clients):
            return  "NAMESERVER SERVING %s" % ', '.join(["%s (%s)" % (c.name, c.address) for c in self.nameserver_clients])
        else:
            return  "NODE"

    def print_tree(self, indent=0):
        print( '%s%s' % (' ' * indent, self))
        childIndent = indent + PRINTMAP_INDENT
        for child in self._get_nodes(recursive=False):
            child.print_tree(indent + PRINTMAP_INDENT)

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

    def _template_file(self):
        if any(self.nodes):
            return "gatewayRouter.jinja2"
        elif self.isNameserver:
            return "nameserver.jinja2"
        else:
            return "node.jinja2"

    def _get_nodes(self, recursive=False):
        nodes = self.nodes[:]
        if recursive:
            for gateway in self.nodes:
                nodes += gateway._get_nodes(recursive=True)
        return nodes

    def _generate_address(self):
        addrParts = self.address.split('.')
        try:
            addrParts[self.maskLength] = str(self.nextAddress)
        except IndexError:
            raise AddressSpaceFullError("The address space is full. Increase max_nodes or ip_address_length")
        address = '.'.join(addrParts)
        self.nextAddress += 1
        return address

    def _full(self):
        return len(self.nodes) >= self.maxNodes

    # Check to see whether the node is a descendent of this one
    def has_descendent(self, node):
        return node in self._get_nodes(recursive=True)

    # Also true if elder is a sibling or even self
    def has_older_family_member(self, elder):
        node = self
        while hasattr(node, 'parent'):
            if node.has_sibling(elder):
                return True
            node = node.parent
        return False

    def descends_from(self, ancestor):
        node = self
        while hasattr(node, 'parent'):
            if node == ancestor:
                return True
            node = node.parent
        return False

    def has_sibling(self, sibling):
        return sibling in self.siblings()

    def is_gateway(self):
        return any(self.nodes)

    def is_nameserver(self):
        return any(self.nameserver_clients)

    def get_network_name(self):
        return '.'.join([loc for loc in self.parent.address.split('.') if loc != '10'])

    def get_subnet_name(self):
        if not self.is_gateway():
            return "NO SUBNET"
        else:
            return self.nodes[0].get_network_name()

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

    def _get_empty_subnet(self):
        for child in self.nodes:
            if not any(child.nodes):
                return child

    def siblings(self):
        return self.parent.nodes if hasattr(self, 'parent') else []

    def _get_recursively_smallest_subnet(self):
        if not any(self.nodes):
            return None
        def smaller(node_one, node_two):
            if len(node_one._get_nodes(True)) <= len(node_two._get_nodes(True)):
                return node_one
            else:
                return node_two
        return reduce(smaller, self.nodes, self.nodes[0])

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
                    
        








    def _mask(self):
        return '.'.join(self.address.split('.')[:self.maskLength])
