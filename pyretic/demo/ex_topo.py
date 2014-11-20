from mininet.topo import Topo

class MyTopo(Topo):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Add links
        self.addLink(s1, h1, bw=2)
        self.addLink(s3, h2, bw=2)
        self.addLink(s1, s2, bw=2)
        self.addLink(s2, s3, bw=2)
        self.addLink(s1, s4, bw=2)
        self.addLink(s4, s3, bw=.1)

topos = {'mytopo': (lambda: MyTopo())}

# HOW TO RUN #
# T1
# pyretic.py pyretic.examples.ft_test
# T2
# sudo mn --custom demo/ex_topo.py --topo mytopo --controller=remote --mac --switch ovsk --link tc
# h2 iperf -s -p 80 &
# h1 iperf -c h2 -p 80
# link s1 s2 down
# h1 iperf -c h2 -p 80
# link s1 s2 up
# h1 iperf -c h2 -p 80
