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
	default_policy1 = if_(match(dstmac = IPAddr('10.0.0.4'), switch = 1), fwd(2), flood())
	default_policy2 = if_(match(dstmac = IPAddr('10.0.0.4'), switch = 2), fwd(2), flood())
	default_policy3 = if_(match(dstmac = IPAddr('10.0.0.4'), switch = 3), fwd(2), flood())	
	default_policy4 = if_(match(dstmac = IPAddr('10.0.0.4'), switch = 4), fwd(2), flood())	
	
	default_policy5 = if_(match(dstmac = IPAddr('10.0.0.1'), switch = 5), fwd(1), flood())
	default_policy6 = if_(match(dstmac = IPAddr('10.0.0.1'), switch = 4), fwd(1), flood())
	default_policy7 = if_(match(dstmac = IPAddr('10.0.0.1'), switch = 3), fwd(1), flood())
	default_policy8 = if_(match(dstmac = IPAddr('10.0.0.1'), switch = 2), fwd(1), flood())	
	
	default_policy = default_policy1 +  default_policy2 +  default_policy3 +  default_policy4 +  default_policy5 +  default_policy6  +  default_policy7 +  default_policy8 
	return default_policy

def main():
	ft_ = ft(define_operator_policy())
	ft_.addft(match(dstport=80,srcmac=EthAddr('00:00:00:00:00:01'),dstmac=EthAddr('00:00:00:00:00:04')), 1, 5)
	#ft_.addft(match(dstport=80,srcmac=EthAddr('00:00:00:00:00:01'),dstmac=EthAddr('00:00:00:00:00:02')), 1, 3)
	return ft_
