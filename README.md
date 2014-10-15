TCP/IP Simulation
=================

This module generates the documents needed for a classroom (or schoolwide) 
simulation of TCP/IP, the protocol that gets packets of information around 
the internet.

Quickstart
----------
To generate the documents you need for a simulation, download this module:

    git clone https://github.com/cproctor/tcp-ip-simulation.git

Then write a little script and save it in the "python" folder.

    studentNames = ['Suzie', 'Liza', 'Emily', 'Ann', 'Chandra', 'Minh Li',
        'Alice', 'Lulu', 'Alejandra', 'Celeste', 'Mia', 'Silvia', 'Diane',
        'Em', 'Jo', 'Gilia', 'Vallen']
    students = [{'name': name} for name in studentNames]
    networks = ["Network %s" % i for i in range(20)]
    sim = TcpIpSimulation(students, networks, nameservers=2, max_nodes=5)
    sim.print_tree()
    sim.generate()

Now you have an HTML file called simulation.html. If you're going to print 
it, you may need to copy it into a word-processor and add line breaks.

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
chris@proctors.us

