################################################################################
# SDN course project, CS8803-SDN, Georgia Tech                                 #
# authors: Aman Mangal(amanmangal@gatech.edu), Vaibhav Malkani, Pragya Agarwal #
################################################################################
# Free to use as long as the authors are notified                              #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.ft import *

def define_operator_policy():
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 1, dstport = 80), fwd(2), flood())
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:01'), switch = 1, inport=2), fwd(1), default_policy)
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 2, dstport = 80), fwd(2), default_policy)
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:01'), switch = 2, inport=2), fwd(1), default_policy)
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 3, dstport = 80), fwd(1), default_policy)
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:01'), switch = 3, inport=1), fwd(2), default_policy)
	return default_policy

def main():
	# ft_ = ft(define_operator_policy())
	# ft_.addft(match(dstport=80), match(srcport=80), 1, 3)
	# return ft_
	return define_operator_policy()
