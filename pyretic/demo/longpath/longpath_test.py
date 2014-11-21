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
    default_policy1 = if_(match(dstip = IPAddr('10.0.0.2'), switch = 1), fwd(2), drop)
    default_policy2 = if_(match(dstip = IPAddr('10.0.0.2'), switch = 4), fwd(2), drop)
    default_policy3 = if_(match(dstip = IPAddr('10.0.0.2'), switch = 2), fwd(1), drop)
    default_policy4 = if_(match(dstip = IPAddr('10.0.0.2'), switch = 3), fwd(1), drop)

    default_policy6 = if_(match(dstip = IPAddr('10.0.0.1'), switch = 1), fwd(1), drop)
    default_policy7 = if_(match(dstip = IPAddr('10.0.0.1'), switch = 4), fwd(1), drop)
    default_policy8 = if_(match(dstip = IPAddr('10.0.0.1'), switch = 2), fwd(2), drop)
    default_policy9 = if_(match(dstip = IPAddr('10.0.0.1'), switch = 3), fwd(2), drop)

    default_policy =  default_policy1 +  default_policy2 +  default_policy3 +  default_policy4 +\
        default_policy6 +  default_policy7 +  default_policy8 +  default_policy9
    return default_policy

def main():
    return define_operator_policy()
