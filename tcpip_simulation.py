from jinja2 import Environment, FileSystemLoader
from random import choice, shuffle
import os

PRINTMAP_INDENT = 4

class TcpIpSimulation(object):
    """Creates docmuentation for a TCP/IP simulation with any size 
    of students."""

    def __init__(self, students, networks, outfile="simulation.html",
            max_nodes=6,
            nameservers=1,
            ip_address_length=2):
        root_address = '.'.join(["100"] * ip_address_length)
        shuffle(students)
        self.outfile = outfile
        self.networks = networks
        self.env = Environment(loader=FileSystemLoader(
                os.path.dirname(os.path.realpath(__file__))))
        self.rootNode = TcpIpGatewayRouter(self.env, 'ROOT', root_address, 
                max_nodes=max_nodes)
        if nameservers > len(students):
            raise ValueError("Not enough students to serve as nameservers")
        for i in range(nameservers):
            self.rootNode.add_node(TcpIpNameserver(
                    self.env, **(students.pop())))
        for student in students:
            node = TcpIpNode(self.env, **student)
            self.rootNode.add_node(node)
        self.assign_nameservers()
        self.update_nameserver_tables()
        self.assign_networks()
        self.assign_partners()

    def print_tree(self):
        print("NETWORK TREE")
        self.rootNode.print_tree()
            
    def generate(self):
        template = self.env.get_template('simulation.jinja2')
        with open(self.outfile, 'w') as outfile:
            outfile.write(template.render(
                    {'nodes': self.rootNode.get_nodes(recursive=True)}))

    def assign_nameservers(self):
        allNodes = self.rootNode.get_nodes(recursive=True)
        nsAddrs = [n.address for n in allNodes if n.isNameserver]
        nodes = [n for n in allNodes if not (n.isNameserver or n.isGateway)]
        for node in nodes:
            node.nameserver = choice(nsAddrs)

    def update_nameserver_tables(self):
        allNodes = self.rootNode.get_nodes(recursive=True)
        lookupTable = {}
        for n in allNodes:
            lookupTable[n.name] = n.address
        for nameserver in [n for n in allNodes if n.isNameserver]:
            nameserver.lookupTable = lookupTable

    def assign_networks(self):
        gateways = [self.rootNode] + [n for n in self.rootNode.get_nodes(recursive=True) 
                if n.isGateway]
        for i, gateway in enumerate(gateways):
            gateway.subnet = self.networks[i]
            gateway.mask = gateway._mask()
            for node in gateway.get_nodes(recursive=False):
                node.network = self.networks[i]

    def assign_partners(self):
        allNodes = self.rootNode.get_nodes(recursive=True)
        nodes = [n for n in allNodes if not(n.isNameserver or n.isGateway)]
        shuffle(nodes)
        for i, node in enumerate(nodes):
            node.round1 = nodes[(i+1) % len(nodes)].name
        shuffle(nodes)
        for i, node in enumerate(nodes):
            node.round2 = nodes[(i+1) % len(nodes)].name
        


class TcpIpNode(object):
    """Represents a node on a network"""
    
    template = 'node.jinja2'
    isGateway = False
    isNameserver = False

    def __init__(self, env, name, address=None):
        self.env = env
        self.name = name
        self.address = address

    def __str__(self):
        return self.env.get_template(self.template).render(self.__dict__)

    def description(self):
        return "%s (%s)" % (self.address, self.name)

    def print_tree(self, indent=0):
        print( ' ' * indent + self.description())
        
class TcpIpGatewayRouter(TcpIpNode):
    """Represents a gateway router."""

    template = 'gatewayRouter.jinja2'
    isGateway = True

    def __init__(self, env, name, address=None, mask_length=0,
                max_nodes=899):
        super(TcpIpGatewayRouter, self).__init__(env, name, address)
        self.maskLength = mask_length
        self.maxNodes = max_nodes
        self.nodes = []
        self.nextAddress = 101

    def description(self):
        #return "%s GATEWAY (%s) %s" % (self.address, self.name, self.__dict__)
        return "%s GATEWAY (%s)" % (self.address, self.name)

    def add_node(self, node):
        if not self.full():
            node.address = self.generate_address()
            self.nodes.append(node)
        else:
            subnet = (  
                self.get_available_subnet() or
                self.create_subnet() or
                self.get_smallest_subnet()
            )
            subnet.add_node(node)            

    def print_tree(self, indent=0):
        super(TcpIpGatewayRouter, self).print_tree(indent)
        childIndent = indent + PRINTMAP_INDENT
        for child in self.get_nodes(recursive=False):
            child.print_tree(childIndent)
            
    def get_nodes(self, recursive=False):
        nodes = self.nodes[:]
        if recursive:
            for gateway in [n for n in self.nodes if n.isGateway]:
                nodes += gateway.get_nodes(recursive=True)
        return nodes

    def generate_address(self):
        addrParts = self.address.split('.')
        addrParts[self.maskLength] = str(self.nextAddress)
        address = '.'.join(addrParts)
        self.nextAddress += 1
        return address

    def full(self):
        return len(self.nodes) >= self.maxNodes

    def get_available_subnet(self):
        for node in self.nodes:
            if node.isGateway and not node.full():
                return node
        return False

    def create_subnet(self):
        foundNode = False
        for target, node in enumerate(self.nodes):
            if not node.isGateway and not node.isNameserver:
                foundNode = True
                break
        if not foundNode:
            return False
        self.nodes[target] = TcpIpGatewayRouter(self.env, node.name, 
                node.address, mask_length=self.maskLength + 1, 
                max_nodes=self.maxNodes)
        return self.nodes[target]

    def get_smallest_subnet(self):
        subnets = [n for n in self.nodes if n.isGateway]
        return sorted(subnets, key=lambda s: len(s.get_nodes(recursive=True)))[0]

    def _mask(self):
        return '.'.join(self.address.split('.')[:self.maskLength])

class TcpIpNameserver(TcpIpNode):
    
    template = 'nameserver.jinja2'
    isNameserver = True

    def description(self):
        return "%s NS (%s)" % (self.address, self.name)

if __name__ == '__main__':
    studentNames = [
        "Lindsey",
        "Sierra",
        "Liv",
        "Jessica",
        "Laniah",
        "Cerys",
        "Valeria",
        "Phoebe",
        "Sydney",
        "Jane",
        "Sarah",
        "Cade",
        "Sode",
        "Reyhaneh",
        "Kayra",
        "Irene",
        "Elena"
]

    students = [{'name': name} for name in studentNames]
    networks = ["Network %s" % i for i in range(20)]
    sim = TcpIpSimulation(students, networks, nameservers=2, max_nodes=5)
    sim.print_tree()
    sim.generate()
