TCP/IP Simulation
=================

This module generates the documents needed for a classroom (or schoolwide) 
simulation of TCP/IP, the protocol that gets packets of information around 
the internet. Use this to generate each player's instructions. You will also 
need to mark out networks with loops of rope or tape on the floor, and lots 
of small scraps of paper--at least ten or twenty per player, each about the size
of an index card. 

To create the physical layout, start by creating Network 0 in the middle of the room
(using rope or tape), with enough room for the students on Network 0 to sit around 
the network. Then, create networks 11, 12, etc. (depending on the settings you used)
so that they touch Network 0 at the middle of the room. If you have additional layers
of subnets, continue to add them as circles touching their parent networks. When we
tried this with 200 students in a gym, the subnets needed to be stretched out as narrow ovals
so there was enough room for everyone.

Quickstart
----------
To generate the documents you need for a simulation, download this module
(type the command below into Terminal):

    git clone https://github.com/cproctor/tcp-ip-simulation.git

Then go into the project, go into the `python` folder, and create a new script:

    cd tcp-ip-simulation
    cd python
    touch my_simulation.py
    open my_simulation.py

Here's some sample code. You may need to fiddle with `max_nodes` and `nodes_per_nameserver`
to find a network that feels good. 

    from tcpip_simulation import TcpIpSimulation

    students_list = ['Suzie', 'Liza', 'Emily', 'Ann', 'Chandra', 'Minh Li',
        'Alice', 'Lulu', 'Alejandra', 'Celeste', 'Mia', 'Silvia', 'Diane',
        'Em', 'Jo', 'Gilia', 'Vallen']
    sim = TcpIpSimulation(
        students_list,
        max_nodes=6,
        nodes_per_nameserver=6,
        ip_address_length=2
    )
    sim.print_tree()
    sim.print_directory()
    sim.generate_instructions()

Run your file by typing `python my_simulation.py` into Terminal. You will see
the network map (gives a good overview of what's going on, but not required for
the simulation) and the directory (you'll need to give a copy of this to each 
nameserver). You now have an HTML file called `simulation.html` containing 
instructions for each student:

    open simulation.html

Overview
--------
In the network simulation, each student will play the role of a node on a 
network (gateway nodes are on two networks). In the classroom, this means 
that students will be scattered around the room, sitting on the floor, 
holding onto a loop of rope (gateway nodes hold two loops).  

Any node may generate a request by filling out a data packet and then 
handing it to another node she is connected to by rope. The FROM and 
TO fields of the data packet must contain an IP address. The MESSAGE
field may contain whatever fits into the box. For example:

    --------------------------------------
    TO:         101.100.100
    FROM:       102.103.100
    MESSAGE:    What is Lulu's IP address?
    --------------------------------------

When a node receives a 
request, she should look at the TO field. If the request is for her, 
she should write a response back to the sender and throw away the 
request. If the request is not for her, she should pass it along to 
the next person. 

Some nodes have special responsibilities. The nameservers have a lookup 
table, translating peoples’ names into IP addresses. When the nameservers
receives a request for a name lookup, she should look up that person’s name 
and return a response containing that person’s name. Gateway nodes are 
responsible for deciding which network they should forward requests to. Each 
gateway node is provided with a subnet mask--a pattern she can use to determine 
whether a request belongs on her network. If a request matches the pattern, it 
should be sent along the subnetwork; otherwise it should be sent along the main 
network.

Encourage the participants to send messages to whomever they want. Sometimes I 
also encourage participants to mess with the system and see what they can get
away with. The goal is to figure out the basic 
mechanics of communication. At the end of the first round, a discussion should 
uncover the following attributes of the system:

- You have to query the nameserver before you can send messages to someone new.
- Packets can take different amounts of time to get to their destination
- There is no way to really know who the message came from. It is possible to 
  spoof other IP addresses. 
- It is possible to see what other people are talking about if you look at packets 
  that are not yours. A really malicious agent could replace packets with new packets,
  and neither the sender nor the receiver would be able to detect it.

If the participants are ready for a greater challenge, ask them to transmit longer 
messages to each other, which don’t fit in a single packet. 
Before this second round, lead a discussion about
creating a protocol to transmit a message broken into several packets, a 
means of putting the messages back in order, and a means of re-requesting any 
packet that gets dropped. 

After the simulation, put students in small groups with different node types, so 
they can discuss their various experiences. If you try this with your students, I 
would love to hear how it went.

-Chris Proctor
chris@chrisproctor.net

