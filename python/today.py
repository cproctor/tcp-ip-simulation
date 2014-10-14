from random import shuffle

#participants = ["Person %s" % (num + 1) for num in range(258)]
participants = ["Person %s" % (num + 1) for num in range(199)]
#shuffle(participants)

from tcpip_simulation import TcpIpSimulation

sim = TcpIpSimulation(
    participants=participants,
    nodes_per_nameserver=7,
    max_nodes=6,
    ip_address_length=3
)

sim.print_tree()
#sim.generate()




