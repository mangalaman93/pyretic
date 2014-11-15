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
    def __init__(self):
    	self.last_topology = None
    	self.backup_policy = None
    	self.flow_dict = {}
    	self.lock = Lock()
        super(ft, self).__init__()

    def addft(self, flow, A, B):
    	# may want to use ip
    	query = packets(None)
    	query.register_callback(self.install_backup_paths)
    	self.flow_dict[(flow, A, B)] = ((flow >> (match(srcmac=A, dstmac=B) + match(srcmac=B, dstmac=A)) >> query), True)
    	if self.backup_policy:
    		self.backup_policy = self.backup_policy + (flow >> (match(srcmac=A, dstmac=B) + match(srcmac=B, dstmac=A)) >> query)
    	else:
    		self.backup_policy = (flow >> (match(srcmac=A, dstmac=B) + match(srcmac=B, dstmac=A)) >> query)

    def __add__(self, pol):
    	self.user_policy = pol
    	return pol + self.backup_policy

    def install_backup_paths(self, pkt):
    	# using some state we will install paths
    	print "inside install back up paths"
    	new_policy = None
    	for k,v in self.flow_dict.items():
    		print k[0].eval(pkt)
    		if v[1]:
    			if k[0].eval(pkt):
	    			self.flow_dict[k] = (v[0], False)
	    		else:
	    			if new_policy:
	    				new_policy = new_policy + v[0]
	    			else:
	    				new_policy = v[0]
	   	self.policy = new_policy

    def set_network(self, network):
    	with self.lock:
    		if self.last_topology is not None:
    			diff_topo = Topology.difference(self.last_topology, network.topology)
    			if diff_topo is not None and len(diff_topo.edges()) == 1:
	    			link = diff_topo.edges()[0]
	    	self.last_topology = network.topology
