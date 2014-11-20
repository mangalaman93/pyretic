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
        video_link_config = {'bw': 50}
        host_link_config = {}

        # Create switch nodes
        for i in range(10):
            sconfig = {'dpid': "%016x" % (i+1)}
            self.addSwitch('s%d' % (i+1), **sconfig)

        # Create host nodes
        for i in range(4):
                self.addHost('h%d' % (i+1), **hconfig)
        #self.addhost('h2', **hconfig)

        # Add switch links
        # Specified to the port numbers to avoid any port number consistency issue

        self.addLink('s1', 'h1', port1=1, port2=1, **video_link_config)
        self.addLink('s1', 's2', port1=2, port2=1, **http_link_config)
        self.addLink('s1', 's6', port1=3, port2=1, **video_link_config)
        self.addLink('s1', 's5', port1=4, port2=4, **video_link_config)

        self.addLink('s2', 's3', port1=2, port2=1, **http_link_config)
        self.addLink('s2', 's7', port1=3, port2=2, **video_link_config)
        self.addLink('s2', 'h2', port1=4, port2=1, **video_link_config)

        self.addLink('s3', 's4', port1=2, port2=1, **http_link_config)
        self.addLink('s3', 's6', port1=3, port2=2, **video_link_config)

        self.addLink('s4', 's5', port1=2, port2=1, **http_link_config)
        self.addLink('s4', 's10', port1=3, port2=2, **video_link_config)

        self.addLink('s5', 'h4', port1=2, port2=1, **video_link_config)
        self.addLink('s5', 's8', port1=3, port2=2, **video_link_config)

        self.addLink('s6', 's7', port1=3, port2=1, **video_link_config)
        self.addLink('s6', 's9', port1=4, port2=1, **video_link_config)

        self.addLink('s7', 's10', port1=3, port2=1, **video_link_config)
        self.addLink('s7', 's8', port1=4, port2=1, **video_link_config)

        self.addLink('s8', 's9', port1=3, port2=2, **video_link_config)
    	self.addLink('s9', 'h3', port1=3, port2=1, **video_link_config)

        info( '\n*** printing and validating the ports running on each interface\n' )

topos = { 'mytopo': ( lambda: FVTopo() ) }
