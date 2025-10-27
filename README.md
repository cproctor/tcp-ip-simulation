# TCP/IP Simulation

TCP/IP is the protocol responsible for routing messages around the
Internet. This package generates everything you need to run a fun and
informative simulation of TCP/IP in your classroom, for any number of
students. We once ran this simulation with 200 students in a gymnasium!

## Installation

This package is installed on PyPI, so you can install it with pip. The simplest way
to install and use this package is with [pipx](https://pipx.pypa.io):

```
% pipx install tcp-ip-simulation
```

## Quickstart

You will need a csv file containing a `name` column, listing the names of all
the participants in the simulation. Then run:

```
% generate-tcp-ip-simulation names.csv
```

This will generate materials for your simulation. 
[Here's an example](sample-tcp-ip-simulation.pdf).

## Options

The `generate-tcp-ip-simulation` command has a number of options you can use to 
tweak your simulation:

```
% generate-tcp-ip-simulation --help

usage: generate [-h] [-l IP_ADDRESS_LENGTH] [-m MAX_NODES]
                [-n NODES_PER_NAMESERVER] [-o OUTFILE] [-r] [-s FIGSIZE]
                participants

Generate materials for a classroom simulation of TCP/IP

positional arguments:
  participants

options:
  -h, --help            show this help message and exit
  -l, --ip-address-length IP_ADDRESS_LENGTH
                        Number of components in IP addresses
  -m, --max-nodes MAX_NODES
                        Maximum nodes per network
  -n, --nodes-per-nameserver NODES_PER_NAMESERVER
                        Maximum nodes per network
  -o, --outfile OUTFILE
                        Path to save result HTML file
  -r, --random          Randomize order of participants
  -s, --figsize FIGSIZE
                        Size of simulation graph
```
