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
	default_policy1 = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), dstport = 80, switch = 1), fwd(2), flood())
	default_policy2 = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), dstport = 80, switch = 2), fwd(3), default_policy1)
	default_policy3 = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), dstport = 80, switch = 3), fwd(2), default_policy2)
	default_policy4 = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), dstport = 80, switch = 4), fwd(2), default_policy3)
	default_policy5 = if_(match(dstmac = EthAddr('00:00:00:00:00:02'), dstport = 80, switch = 5), fwd(2), default_policy4)

	default_policy6 = if_(match(dstmac = EthAddr('00:00:00:00:00:01'), srcport = 80, switch = 5), fwd(1), default_policy5)
	default_policy7 = if_(match(dstmac = EthAddr('00:00:00:00:00:01'), srcport = 80, switch = 4), fwd(1), default_policy6)
	default_policy8 = if_(match(dstmac = EthAddr('00:00:00:00:00:01'), srcport = 80, switch = 3), fwd(1), default_policy7)
	default_policy9 = if_(match(dstmac = EthAddr('00:00:00:00:00:01'), srcport = 80, switch = 2), fwd(1), default_policy8)
	default_policy = if_(match(dstmac = EthAddr('00:00:00:00:00:01'), srcport = 80, switch = 1), fwd(1), default_policy9)

	return default_policy

def main():
	ft_ = ft(define_operator_policy())
	ft_.addft(match(dstport=80), match(srcport=80), 1, 3)
	return ft_
