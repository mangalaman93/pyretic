################################################################################
# SDN course project, CS8803-SDN, Georgia Tech                                 #
# authors: Aman Mangal(amanmangal@gatech.edu), Vaibhav Malkani, Jessie McGarry #
################################################################################
# Free to use as long as the authors are notified                              #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.ft import *

def define_operator_policy():
    default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 1), fwd(1), flood())
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 2), fwd(2), default_policy)
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 4), fwd(4), default_policy)
	return default_policy

def main():
	return define_operator_policy()

