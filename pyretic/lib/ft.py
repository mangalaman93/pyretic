################################################################################
# SDN course project, CS8803-SDN, Georgia Tech                                 #
# authors: Aman Mangal(amanmangal@gatech.edu), Vaibhav Malkani, Jessie McGarry #
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
#   failures as of now
# *middle rule does not get installed unless the extreme rules are installed

# Caution #
# *remember to match incoming direction in the rule to avoid loops
# *make sure that class we define are in itself policies
# *make sure that the back up paths we install does not conflict with
#   the existing policy (normal policy, policy without fault tolerance
#   policy)
# *handle dynamic policies

# four modes of fault tolerance #
# of1.0: proactive; use if switches do not support openFlow 1.3
# of1.3: proactive; use if switches support openFlow 1.3 (group tables will
#		 will be used)
# rr   : reactive-reactive; when a link fails, existing rules are deleted.
# 		 if a new packet for the corresponding flow comes, we install
# 		 back up paths (as new rules) in the switches
# rp   : reactive-proactive; when a link fails, existing rules are deleted
#		 and new rules are installed pro-actively even before a packet
#        comes for the corresponding flow

# How to specify fault tolerance #
# *specify list of links not to use as back up paths (global)
# *specify list of links preferred to use as back up paths (global)
# *compose fault tolerance policy class with the normal policy while
#   specifying flow and nodes so that path for the flow can be made
#   fault tolerant with degree 1

class ft(DynamicPolicy):
    def __init__(self, pol):
    	super(ft, self).__init__()
    	self.last_topology = None  # stores last topology
    	self.flow_dict = {} 	   # stores ?
    	self.user_policy = pol     # stores user policy
    	self.lock = Lock()
        self.policy = pol

    def addft(self, flow, A, B):
    	# may want to use ip as well later
    	query = packets(None)
    	# registers call back for installing back up path when first packet corresponding to
    	#  the flow comes into the network and hence controller
    	query.register_callback(self.install_backup_paths)
    	final_query = (flow >> (match(srcmac=A, dstmac=B) + match(srcmac=B, dstmac=A)) >> query)
    	self.flow_dict[(flow, A, B)] = (final_query, True)
    	self.policy = self.policy + final_query

    def install_backup_paths(self, pkt):
    	new_policy = self.user_policy
    	# iterating over all flow and correspoding handlers in the table
    	for k,v in self.flow_dict.items():
    		flag = True
    		for x,y in k[0].map.iteritems():
    			flag = flag and (pkt[x] == y)
    		# if back up policy is already not installed
    		if v[1]:
    			if flag:
	    			self.flow_dict[k] = (v[0], False)
	    		else:
	    			new_policy = new_policy + v[0]
	   	self.policy = new_policy

    def set_network(self, network):
    	with self.lock:
    		if self.last_topology is not None:
    			diff_topo = Topology.difference(self.last_topology, network.topology)
    			if diff_topo is not None and len(diff_topo.edges()) == 1:
	    			link = diff_topo.edges()[0]
	    	self.last_topology = network.topology
