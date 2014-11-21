===========
Pyretic FT
===========
Pyretic fault tolerance library. Compose with ```ft``` and make your policy fault tolerant!

# How to Run
* download the code in the branch ```ft-course```
* compose the policy with ```ft``` class of pyretic
* add call to ```addft()``` and specify flows and end-points (switches only)

# Assumptions
* independent flows while calling ```addft()```
* does not handle multiple link failures at a time

# Example code
```
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
        ft_ = ft(define_operator_policy())
        ft_.addft(match(dstport=80), match(srcport=80), 1, 3)
        return ft_
```

# Resources
* [presentaion slides](https://docs.google.com/presentation/d/1N9EVEuB2OxQNqZRKbTEL0ohV1LyfH-8UKIENoxj0V9o)
* example run [video](http://youtu.be/O0ZTQYlPsaI)

# Example run

## Demo 1 - Choose the path(s) minimizing total rules
* Start the controller 
```
cd ~/pyretic
pyretic.py pyretic.demo.conflict.conflict_test
```
* Start mininet in the other terminal and execute the following commands. Observe that after the link goes down, the traffic does not flow from h1 to h2.
```
cd ~/pyretic
sudo mn --custom pyretic/demo/conflict/conflictTopo.py --topo mytopo --switch ovsk --link tc --controller=remote --mac
h2 iperf -s -p 80 &
h1 iperf -c h2 -p 80
link s2 s3 down
h1 iperf -c h2 -p 80
```
* Stop the controller and start another one with ft
```
pyretic.py pyretic.demo.conflict.conflict_test_with_ft
```
* Test with mininet again. Observe that even after the link goes down, the traffic flows from h1 to h2. The traffic flows from the high bandwidth path.
```
link s2 s3 up
h1 iperf -c h2 -p 80
link s2 s3 down
h1 iperf -c h2 -p 80
```

## Demo 2 - Not full graph search
* Start the controller 
```
cd ~/pyretic
pyretic.py pyretic.demo.longpath.longpath_test
```
* Start mininet in the other terminal and execute the following commands. Observe that after the link goes down, the traffic does not flow from h1 to h2.
```
cd ~/pyretic
sudo python pyretic/demo/longpath/longpathTopo.py 8 3 4
h2 iperf -s -p 80 &
h1 iperf -c h2 -p 80
link s1 s4 down
h1 iperf -c h2 -p 80
```
* Stop the controller and start another one with ft
```
pyretic.py pyretic.demo.longpath.longpath_test_with_ft
```
* Test with mininet again. Observe that even after the link goes down, the traffic flows from h1 to h2.
```
link s1 s4 up
h1 iperf -c h2 -p 80
link s1 s4 down
h1 iperf -c h2 -p 80
```



##
