################################################################################
# SDN course project, CS8803-SDN, Georgia Tech                                 #
# authors: Aman Mangal(amanmangal@gatech.edu), Vaibhav Malkani, Jessie McGarry #
################################################################################
# Free to use as long as the authors are notified                              #
################################################################################

"""Pyretic Library for Fault Tolerance"""
from pyretic.lib.corelib import *
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
        super(ft, self).__init__()
