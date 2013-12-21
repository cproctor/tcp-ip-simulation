TCP/IP Simulation
=================

This module generates the documents needed for a classroom (or schoolwide) 
simulation of TCP/IP, the protocol that gets packets of information around 
the internet.

Quickstart
----------
    studentNames = ['Suzie', 'Liza', 'Emily', 'Ann', 'Chandra', 'Minh Li',
        'Alice', 'Lulu', 'Alejandra', 'Celeste', 'Mia', 'Silvia', 'Diane',
        'Em', 'Jo', 'Gilia', 'Vallen']
    students = [{'name': name} for name in studentNames]
    networks = ["Network %s" % i for i in range(20)]
    sim = TcpIpSimulation(students, networks, nameservers=2, max_nodes=5)
    sim.print_tree()
    sim.generate()

Overview
--------
In the network simulation, each student will play the role of a node on a 
network (gateway nodes are on two networks). In the classroom, this means 
that students will be scattered around the room, sitting on the floor, 
holding onto a loop of rope (gateway nodes hold two loops).  

Any node may generate a request by filling out a data packet and then 
handing it to another node she is connected to by rope. The FROM and 
TO fields of the data packet must contain an IP address. The CONTENT 
field may contain whatever fits into the box. When a node receives a 
request, she should look at the TO field. If the request is for her, 
she should write a response back to the sender and throw away the 
request. If the request is not for her, she should pass it along to 
the next person. 

Some nodes have special responsibilities. The Name Server(s) has a lookup 
table, translating peoples’ names into IP addresses. When the Name Server(s) 
receives a request for a name lookup, she should look up that person’s name 
and return a response containing that person’s name. Gateway nodes are 
responsible for deciding which network they should forward requests to. Each 
gateway node is provided with a subnet mask--a pattern she can use to determine 
whether a request belongs on her network. If a request matches the pattern, it 
should be sent along the subnetwork; otherwise it should be sent along the main 
network.

There are two rounds of the simulation. In the first round (about 8 minutes), 
students simply chat with one another. Each student has an assigned chat 
partner, but may chat with others as well. The goal is to figure out the basic 
mechanics of communication. At the end of the first round, a discussion should 
uncover the following attributes of the system:

- You have to query the nameserver before you can send messages to someone new.
- Packets can take different paths to arrive at their destinations, and can take 
  different amounts of time to get there.
- If any rope were cut somewhere, packets would still be able to get to get to 
  their destinations.
- There is no way to really know who the message came from. It is possible to 
  spoof other IP addresses. 
- It is possible to see what other people are talking about if you look at packets 
  that are not yours. 

In the second round, students will be required to transmit longer messages to each 
other, which don’t fit in a single packet. If students are doing well, you could 
steal some packets (or possibly even 
knock a few nodes offline). Before the second round, lead a discussion with 
students creating a protocol to transmit a message broken into several packets, a 
means of putting the messages back in order, and a means of re-requesting any 
packet that gets dropped. Then start the second round. 

After the simulation, put students in small groups with different node types, so 
they can discuss their various experiences. If you try this with your students, I 
would love to hear how it went.

-Chris Proctor
chris@proctors.us

