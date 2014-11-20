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
	default_policy1 = match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 1) >> fwd(3)
	default_policy2 = match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 2) >> fwd(2)
	default_policy3 = match(dstmac = EthAddr('00:00:00:00:00:02'), switch = 3) >> fwd(3)

	default_policy5 = match(dstmac = EthAddr('00:00:00:00:00:01'), switch = 4) >> fwd(1)
	default_policy6 = match(dstmac = EthAddr('00:00:00:00:00:01'), switch = 3) >> fwd(1)
	default_policy7 = match(dstmac = EthAddr('00:00:00:00:00:01'), switch = 2) >> fwd(1)

	default_policy = default_policy1 +  default_policy2 +  default_policy3 +  default_policy5 +  default_policy6  +  default_policy7
	return default_policy

def main():
	ft_ = ft(define_operator_policy())
	ft_.addft(match(dstport=80,srcmac=EthAddr('00:00:00:00:00:01'),dstmac=EthAddr('00:00:00:00:00:02')), 1, 4)
	return ft_
