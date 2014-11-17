################################################################################
# SDN course project, CS8803-SDN, Georgia Tech                                 #
# authors: Aman Mangal(amanmangal@gatech.edu), Vaibhav Malkani, Pragya Agarwal #
################################################################################
# Free to use as long as the authors are notified                              #
################################################################################

"""Pyretic Library for Fault Tolerance"""
from multiprocessing import Lock
from pyretic.lib.corelib import *
from pyretic.lib.query import *
from pyretic.lib.std import *

# Assumptions #
# *assume only one link fails at a time, we don't optmize for multiple link
#   failures at a time as of now

# Caution #
# *remember to match incoming direction in the rule to avoid loops
# *^what about the rules already installed, they should not have
#  incoming node as part of the rules itself
# *make sure that the back up paths we install do not conflict with
#   the existing policy (normal policy, policy without fault tolerance
#   policy)
# *handle dynamic policies

# How to specify fault tolerance #
# *specify list of links not to use as back up paths (global)
# *specify list of links preferred to use as back up paths (global)

class ft(DynamicPolicy):
    def __init__(self, pol):
    	super(ft, self).__init__()
    	self.last_topology = None  # stores last topology
    	self.flow_dict = {} 	   # stores everything related to ft
    	self.user_policy = pol     # stores user policy
    	self.lock = Lock()
        self.policy = self.user_policy

    def addft(self, flow, A, B):
    	if not isinstance(flow, match):
    		raise Exception("unknown flow type in addft function call")
    	if isinstance(A, EthAddr) or (isinstance(A, str) and A.count(':')==5):
            matchA = match(srcmac=EthAddr(A)) + match(dstmac=EthAddr(A))
        elif isinstance(A, IPAddr) or (isinstance(A, str) and A.count('.')==3):
        	matchA = match(srcip=A) + match(dstip=A)
        else:
        	raise Exception("Error: unknown node type in addft function call")

        if isinstance(B, EthAddr) or (isinstance(B, str) and B.count(':')==5):
            matchB = match(srcmac=EthAddr(B)) + match(dstmac=EthAddr(B))
        elif isinstance(B, IPAddr) or (isinstance(B, str) and B.count('.')==3):
        	matchB = match(srcip=B) + match(dstip=B)
        else:
        	raise Exception("Error: unknown node type in addft function call")

    	# registers call back for installing back up path when first packet corresponding to
    	#  the flow comes into the network and hence to controller
    	query = packets(None)
    	query.register_callback(self.install_backup_paths)
    	filtered_query = flow >> matchA >> matchB >> query
    	self.flow_dict[(flow, A, B)] = (filtered_query, True, dict(), dict())
    	self.policy = self.policy + filtered_query

    def install_backup_paths(self, pkt):
    	with self.lock:
	    	new_policy = self.user_policy
	    	# iterating over all flow and correspoding handlers in the table
	    	# key=(flow, A, B) & value=(policy, flag, reactive_pol, proactive_pol)
	    	# flag => whether back up paths for the flow are installed already
	    	for key,value in self.flow_dict.items():
	    		# if back up policy is already not installed
    			if value[1]:
    				# if flow corresponds to current back up path
    				try:
						flag = True
						for x,y in key[0].map.iteritems():
							flag = flag and (pkt[x] == y)
    				except:
						flag = False
					# then removing handlers for the packet
	    			if flag:
	    				self.flow_dict[key] = (value[0], False) + value[2:]
	    				# and install backup paths
		    		else:
		    			new_policy = new_policy + value[0]
	   		self.policy = new_policy

    def set_network(self, network):
    	with self.lock:
    		if self.last_topology is not None:
    			diff_topo = Topology.difference(self.last_topology, network.topology)
    			if diff_topo is not None and len(diff_topo.edges()) == 1:
	    			failed_link = diff_topo.edges()[0]
	    		elif diff_topo is None:
	    			print "the topology didn't change!"
	    		else:
	    			print "we don't handle this case as of now"
	    	self.last_topology = network.topology
