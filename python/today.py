studentNames = [
"Giselle Hernandez Arana",
"Cate Celio",
"Valerie Braylovskiy",
"Isabelle Ancajas",
"Ellie Budde",
"Anne Friedman",
"Sofia Akhtar",
"Carlie Malott",
"Gwyneth Wong",
"Sadie Fernandez",
"Emily Gatica",
"Grace Huber",
"Sahana Singh",
"Anna Finlay",
"Tiffany Sanchez",
"Anna Majorek",
"Roohi Joshi"
]

students = [{"name": name} for name in studentNames]
networks = ["Network %s" % (netNum + 1) for netNum in range(4)]

from tcpip_simulation import TcpIpSimulation

sim = TcpIpSimulation(
    students=students,
    networks=networks,
    nameservers=2,
    max_nodes=5
)

sim.print_tree()
sim.generate()




