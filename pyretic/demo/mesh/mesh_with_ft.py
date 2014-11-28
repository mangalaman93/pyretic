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
    default_policy1 = if_(match(srcip = IPAddr('10.0.0.1'),dstip = IPAddr('10.0.0.3'), switch = 1), fwd(1), drop)
    default_policy2 = if_(match(srcip = IPAddr('10.0.0.1'),dstip = IPAddr('10.0.0.3'), switch = 2), fwd(2), drop)
    default_policy3 = if_(match(srcip = IPAddr('10.0.0.1'),dstip = IPAddr('10.0.0.3'), switch = 3), fwd(4), drop)
    rdefault_policy1 = if_(match(srcip = IPAddr('10.0.0.3'),dstip = IPAddr('10.0.0.1'), switch = 1), fwd(3), drop)
    rdefault_policy2 = if_(match(srcip = IPAddr('10.0.0.3'),dstip = IPAddr('10.0.0.1'), switch = 2), fwd(1), drop)
    rdefault_policy3 = if_(match(srcip = IPAddr('10.0.0.3'),dstip = IPAddr('10.0.0.1'), switch = 3), fwd(1), drop)

    default_policy4 = if_(match(srcip = IPAddr('10.0.0.1'),dstip = IPAddr('10.0.0.4'), switch = 1), fwd(2), drop)
    default_policy5 = if_(match(srcip = IPAddr('10.0.0.1'),dstip = IPAddr('10.0.0.4'), switch = 8), fwd(4), drop)
    default_policy6 = if_(match(srcip = IPAddr('10.0.0.1'),dstip = IPAddr('10.0.0.4'), switch = 7), fwd(3), drop)
    rdefault_policy4 = if_(match(srcip = IPAddr('10.0.0.4'),dstip = IPAddr('10.0.0.1'), switch = 1), fwd(3), drop)
    rdefault_policy5 = if_(match(srcip = IPAddr('10.0.0.4'),dstip = IPAddr('10.0.0.1'), switch = 8), fwd(1), drop)
    rdefault_policy6 = if_(match(srcip = IPAddr('10.0.0.4'),dstip = IPAddr('10.0.0.1'), switch = 7), fwd(2), drop)

    default_policy7 = if_(match(srcip = IPAddr('10.0.0.4'),dstip = IPAddr('10.0.0.2'), switch = 7), fwd(1), drop)
    default_policy8 = if_(match(srcip = IPAddr('10.0.0.4'),dstip = IPAddr('10.0.0.2'), switch = 6), fwd(1), drop)
    default_policy9 = if_(match(srcip = IPAddr('10.0.0.4'),dstip = IPAddr('10.0.0.2'), switch = 5), fwd(5), drop)
    rdefault_policy7 = if_(match(srcip = IPAddr('10.0.0.2'),dstip = IPAddr('10.0.0.4'), switch = 7), fwd(3), drop)
    rdefault_policy8 = if_(match(srcip = IPAddr('10.0.0.2'),dstip = IPAddr('10.0.0.4'), switch = 6), fwd(2), drop)
    rdefault_policy9 = if_(match(srcip = IPAddr('10.0.0.2'),dstip = IPAddr('10.0.0.4'), switch = 5), fwd(4), drop)

    default_policy10 = if_(match(srcip = IPAddr('10.0.0.2'),dstip = IPAddr('10.0.0.3'), switch = 5), fwd(1), drop)
    default_policy11 = if_(match(srcip = IPAddr('10.0.0.2'),dstip = IPAddr('10.0.0.3'), switch = 4), fwd(1), drop)
    default_policy12 = if_(match(srcip = IPAddr('10.0.0.2'),dstip = IPAddr('10.0.0.3'), switch = 3), fwd(4), drop)
    rdefault_policy10 = if_(match(srcip = IPAddr('10.0.0.3'),dstip = IPAddr('10.0.0.2'), switch = 5), fwd(5), drop)
    rdefault_policy11 = if_(match(srcip = IPAddr('10.0.0.3'),dstip = IPAddr('10.0.0.2'), switch = 4), fwd(3), drop)
    rdefault_policy12 = if_(match(srcip = IPAddr('10.0.0.3'),dstip = IPAddr('10.0.0.2'), switch = 3), fwd(2), drop)

    default_policy13 = if_(match(srcip = IPAddr('10.0.0.1'),dstip = IPAddr('10.0.0.5'), switch = 1), fwd(1), drop)
    default_policy14 = if_(match(srcip = IPAddr('10.0.0.1'),dstip = IPAddr('10.0.0.5'), switch = 2), fwd(5), drop)
    rdefault_policy13 = if_(match(srcip = IPAddr('10.0.0.5'),dstip = IPAddr('10.0.0.1'), switch = 1), fwd(3), drop)
    rdefault_policy14 = if_(match(srcip = IPAddr('10.0.0.5'),dstip = IPAddr('10.0.0.1'), switch = 2), fwd(1), drop)

    default_policy15 = if_(match(srcip = IPAddr('10.0.0.4'),dstip = IPAddr('10.0.0.6'), switch = 7), fwd(1), drop)
    default_policy16 = if_(match(srcip = IPAddr('10.0.0.4'),dstip = IPAddr('10.0.0.6'), switch = 6), fwd(3), drop)
    rdefault_policy15 = if_(match(srcip = IPAddr('10.0.0.6'),dstip = IPAddr('10.0.0.4'), switch = 7), fwd(3), drop)
    rdefault_policy16 = if_(match(srcip = IPAddr('10.0.0.6'),dstip = IPAddr('10.0.0.4'), switch = 6), fwd(2), drop)

    default_policy17 = if_(match(srcip = IPAddr('10.0.0.3'),dstip = IPAddr('10.0.0.7'), switch = 3), fwd(2), drop)
    default_policy18 = if_(match(srcip = IPAddr('10.0.0.3'),dstip = IPAddr('10.0.0.7'), switch = 4), fwd(4), drop)
    rdefault_policy17 = if_(match(srcip = IPAddr('10.0.0.7'),dstip = IPAddr('10.0.0.3'), switch = 3), fwd(4), drop)
    rdefault_policy18 = if_(match(srcip = IPAddr('10.0.0.7'),dstip = IPAddr('10.0.0.3'), switch = 4), fwd(1), drop)

    def_p =  default_policy1 + default_policy2 + default_policy3 + default_policy4 + default_policy5 + default_policy6 +\
             default_policy7 + default_policy8 + default_policy9 + default_policy10 + default_policy11 + default_policy12 +\
             default_policy13 + default_policy14 + default_policy15 + default_policy16  + default_policy17 + default_policy18
    rdef_p =  rdefault_policy1 + rdefault_policy2 + rdefault_policy3 + rdefault_policy4 + rdefault_policy5+ rdefault_policy6 +\
              rdefault_policy7 + rdefault_policy8 + rdefault_policy9 + rdefault_policy10 + rdefault_policy11 +\
              rdefault_policy12 + rdefault_policy13 + rdefault_policy14 + rdefault_policy15 + rdefault_policy16 +\
              rdefault_policy17 + rdefault_policy18

    default_policy = def_p + rdef_p
    return default_policy

def main():
    ft_ = ft(define_operator_policy())
    ft_.addft(match(dstport=80, dstip=IPAddr('10.0.0.3')),match(srcport=80, srcip=IPAddr('10.0.0.1')), 1, 3)
    ft_.addft(match(dstport=8000,dstip = IPAddr('10.0.0.5')),match(srcport=8000,srcip=IPAddr('10.0.0.1')), 1, 2)
    ft_.addft(match(dstport=9000),match(srcport=9000), 7, 5)
    ft_.addft(match(dstport=80,dstip = IPAddr('10.0.0.2')),match(srcport=80,srcip=IPAddr('10.0.0.3')), 3, 5)
    ft_.addft(match(dstport=80,dstip = IPAddr('10.0.0.4')),match(srcport=80,srcip=IPAddr('10.0.0.2')), 5, 7)
    ft_.addft(match(dstport=80,dstip = IPAddr('10.0.0.6')),match(srcport=80,srcip=IPAddr('10.0.0.4')), 7, 6)
    ft_.addft(match(dstport=80,srcmac=EthAddr('00:00:00:00:00:01'),dstmac=EthAddr('00:00:00:00:00:02')),
              match(srcport=80,dstmac=EthAddr('00:00:00:00:00:01'),srcmac=EthAddr('00:00:00:00:00:02')), 1, 3)
    return ft_
