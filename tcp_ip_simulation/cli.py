import csv
from random import shuffle
from argparse import ArgumentParser
from tcp_ip_simulation.tcp_ip_simulation import TcpIpSimulation

def generate():
    parser = ArgumentParser(
        prog="generate",
        description="Generate materials for a classroom simulation of TCP/IP"
    )
    parser.add_argument("participants")
    parser.add_argument("-l", "--ip-address-length", default=3, type=int,
            help="Number of components in IP addresses")
    parser.add_argument("-m", "--max-nodes", default=6, type=int,
            help="Maximum nodes per network")
    parser.add_argument("-n", "--nodes-per-nameserver", default=6, type=int,
            help="Maximum nodes per network")
    parser.add_argument("-o", "--outfile", default="simulation.html", 
            help="Path to save result HTML file")
    parser.add_argument("-r", "--random", action="store_true",
            help="Randomize order of participants")
    args = parser.parse_args()
    
    with open(args.participants) as fh:
        reader = csv.DictReader(fh)
        if "name" not in reader.fieldnames:
            raise ValueError("CSV file must contain a 'name' column")
        data = list(reader)
    
    participants = [row['name'] for row in data]
    if args.random:
        shuffle(participants)
    sim = TcpIpSimulation(
        participants, 
        outfile=args.outfile,
        max_nodes=args.max_nodes,
        nodes_per_nameserver=args.nodes_per_nameserver,
        ip_address_length=args.ip_address_length,
    )
    sim.generate_instructions()
