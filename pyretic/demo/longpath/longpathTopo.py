import inspect
import os
import sys
import atexit
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.topo import SingleSwitchTopo
from mininet.node import RemoteController

# sudo python longpath.py 8 3 4

net = None

class FVTopo(Topo):
    # credit: https://github.com/onstutorial/onstutorial/blob/master/flowvisor_scripts/flowvisor_topo.py
    def __init__(self,k,m,b):
        # Initialize topology
        Topo.__init__(self,k)
        #print "The value is %d" % k
        # Create template host, switch, and link
        hconfig = {'inNamespace':True}
        http_link_config = {'bw': 10}
        video_link_config = {'bw': 50}
        host_link_config = {}

        total_switches = b*k + m + 3

        # Create switch nodes
        for i in range(total_switches):
            sconfig = {'dpid': "%016x" % (i+1)}
            self.addSwitch('s%d' % (i+1), **sconfig)

        # Create host nodes
        for i in range(2):
            self.addHost('h%d' % (i+1), **hconfig)

        # Add switch links
        # Specified to the port numbers to avoid any port number consistency issue
        self.addLink('s1', 'h1', port1=1, port2=1, **video_link_config)
        counter = 3
        portnum = 2
        for i in range(b):
            counter = counter + 1
            self.addLink('s1', 's%d' %(counter), port1=portnum, port2=1, **video_link_config)
            for j in range(k-1):
                 print "I AM HERE connecting %d " % counter
                 self.addLink('s%d' % (counter), 's%d' %(counter+1), port1=2, port2=1, **http_link_config)
                 counter = counter +1
            self.addLink('s%d' % (counter), 's2', port1=2, port2=portnum, **video_link_config)
            portnum = portnum + 1

        counter = counter + 1
        self.addLink('s1', 's%d' % (counter), port1=portnum, port2=1, **video_link_config)
        for i in range(m-1):
            self.addLink('s%d' % (counter), 's%d' %(counter+1), port1=2, port2=1, **video_link_config)
            counter = counter + 1
        self.addLink('s%d' % (counter), 's3', port1=2, port2=3, **video_link_config)
        self.addLink('s3', 'h2', port1=1, port2=1, **video_link_config)
        self.addLink('s2', 's3', port1=1, port2=2, **video_link_config)

        info( '\n*** printing and validating the ports running on each interface\n' )

def startNetwork(k,m,b):
    info('** Creating Overlay network topology\n')
    topo = FVTopo(k,m,b)
    global net
    net = Mininet(topo=topo, link = TCLink,
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
    k = int(sys.argv[1])
    m = int(sys.argv[2])
    b = int(sys.argv[3])
    startNetwork(k,m,b)

topos = { 'mytopo': ( lambda: FVTopo() ) }
