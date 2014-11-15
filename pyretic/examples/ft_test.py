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
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 1, dstport = 80), fwd(2), flood())		
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 2, dstport = 80), fwd(2), default_policy)		
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 3, dstport = 80), fwd(1), default_policy)		
	return default_policy

def main():
	ft_ = ft()
	ft_.addft(match(dstport=80), EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:02'))
	return ft_ + define_operator_policy()
