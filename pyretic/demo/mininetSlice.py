#!/usr/bin/python

"""
Coursera:
- Software Defined Networking (SDN) course
-- Network Virtualization: Network Topology

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta
"""

import inspect
import os
import atexit
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.topo import SingleSwitchTopo
from mininet.node import RemoteController

net = None

class FVTopo(Topo):
    # credit: https://github.com/onstutorial/onstutorial/blob/master/flowvisor_scripts/flowvisor_topo.py
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        hconfig = {'inNamespace':True}
        http_link_config = {'bw': 10}
        video_link_config = {'bw': 100}
        host_link_config = {}

        # Create switch nodes
        for i in range(4):
            sconfig = {'dpid': "%016x" % (i+1)}
            self.addSwitch('s%d' % (i+1), **sconfig)

        # Create host nodes
        for i in range(2):
        	self.addHost('h%d' % (i+1), **hconfig)
	#self.addhost('h2', **hconfig)

        # Add switch links
        # Specified to the port numbers to avoid any port number consistency issue
        
        self.addLink('s2', 's1', port1=1, port2=2, **http_link_config)
        self.addLink('s4', 's1', port1=1, port2=3, **video_link_config)
        self.addLink('h1', 's1', port1=1, port2=1, **host_link_config)
        
        self.addLink('s2', 's3', port1=2, port2=2, **http_link_config)
        self.addLink('s4', 's3', port1=2, port2=3, **video_link_config)
        self.addLink('h2', 's3', port1=1, port2=1, **host_link_config)
        
        info( '\n*** printing and validating the ports running on each interface\n' )
        

topos = { 'mytopo': ( lambda: FVTopo() ) }
'''def startNetwork():
    info('** Creating Overlay network topology\n')
    topo = FVTopo()
    global net
    net = Mininet(topo=topo, link = TCLink, switch = ovsk, 
                  controller=lambda name: RemoteController(name, ip='127.0.0.1'),
                  listenPort=6633, autoSetMacs=True)

    info('** Starting the network\n')
    net.start()


    info('** Running CLI\n')
    CLI(net)


def stopNetwork():
    if net is not None:
        info('** Tearing down Overlay network\n')
        net.stop()

if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()
'''
