################################################################################
# SDN course project, CS8803-SDN, Georgia Tech                                 #
# authors: Aman Mangal(amanmangal@gatech.edu), Vaibhav Malkani, Pragya Agarwal #
################################################################################
# Free to use as long as the authors are notified                              #
################################################################################

"""Pyretic Library for Fault Tolerance"""
from multiprocessing import Lock
from pyretic.lib.corelib import *
from pyretic.lib.query import *
from pyretic.lib.std import *

# Assumptions #
# *assume only one link fails at a time, we don't optmize for multiple link
#   failures at a time as of now
# *we only make switch attached to host A TO switch attached to host B path
#   fault tolerant. Also we assume that one host is only attached to one
#   switch only, not more than one switched

# Caution #
# *remember to match incoming direction in the rule to avoid loops
# *^what about the rules already installed, they should not have
#  incoming node as part of the rules itself
# *make sure that the back up paths we install do not conflict with
#   the existing policy (normal policy, policy without fault tolerance
#   policy)
# *handle dynamic policies

# How to specify fault tolerance #
# *specify list of links not to use as back up paths (global)
# *specify list of links preferred to use as back up paths (global)

class ft(DynamicPolicy):
    def __init__(self, pol):
        super(ft, self).__init__()
        self.last_topology = None  # stores last topology
        self.flow_dict = {}        # stores everything related to ft
        self.user_policy = pol     # stores user policy
        self.lock = Lock()
        self.policy = self.user_policy

    def addft(self, Flow, Source, Goal):
        if not isinstance(Flow, match):
            raise Exception("unknown flow type in addft function call")

        if isinstance(Source, int):
            matchA = match(switch=Source)
        else:
            raise Exception("Error: unknown node type in addft function call")

        if isinstance(Goal, int):
            matchB = match(switch=Goal)
        else:
            raise Exception("Error: unknown node type in addft function call")

        # registers call back for installing back up path when first packet corresponding to
        #  the flow comes into the network and hence to controller
        query = packets(None)
        query.register_callback(self.install_backup_paths)
        filtered_query = Flow >> (matchA + matchB) >> query
        self.flow_dict[(Flow, Source, Goal)] = (filtered_query, True, dict(), dict())
        self.policy = self.policy + filtered_query

    def install_backup_paths(self, pkt):
        with self.lock:
            new_policy = self.user_policy
            # iterating over all flow and correspoding handlers in the table
            # key=(flow, source, goal) & value=(policy, flag, reactive_pol, proactive_pol)
            # flag => whether back up paths for the flow are installed already
            for key,value in self.flow_dict.items():
                # if back up policy is already not installed
                if value[1]:
                    try:
                        flag = True
                        for x,y in key[0].map.iteritems():
                            flag = flag and (pkt[x] == y)
                    except:
                        flag = False

                    # if pkt corresponds to current flow
                    if flag:
                        current_path = self.compute_current_path(pkt, key[2])
                        # if unable to compute backup path => skip
                        if current_path == []:
                            return
                        else:
                            #

                    # removing handlers for the packet
                    if flag:
                        self.flow_dict[key] = (value[0], False) + value[2:]
                    else:
                        new_policy = new_policy + value[0]
            self.policy = new_policy

    def set_network(self, network):
        with self.lock:
            if self.last_topology is not None:
                diff_topo = Topology.difference(self.last_topology, network.topology)
                if diff_topo is not None and len(diff_topo.edges()) == 1:
                    failed_link = diff_topo.edges()[0]
                elif diff_topo is None:
                    print "the topology didn't change!"
                else:
                    print "we don't handle this case as of now"
            self.last_topology = network.topology

    # helper functions
    def compute_current_path(self, pkt, goal):
        try:
            current_path = []
            new_pkt = pkt
            while new_pkt["switch"]!=goal:
                cpkts = self.user_policy.eval(new_pkt)
                if len(cpkts) == 1:
                    pkt = new_pkt
                    new_pkt = list(cpkts)[0]
                else:
                    return []

                next_switch = self.last_topology.node[pkt["switch"]]["ports"][new_pkt["outport"]].linked_to
                if next_switch is None:
                    return []
                current_path.append(pkt["switch"])
                new_pkt.modifymany({"switch":next_switch})
        except:
            return []

    def compute_ft_links(self, path, current):
        to_del_index = []
        for i,n1 in enumerate(path):
          for j,n2 in enumerate(current):
              if n1 == n2:
                  if i+1<len(path) and (j+1)<len(current) and path[i+1]==current[j+1]:
                      to_del_index.append(j)
        return [val for i,val in enumerate(current[:-1]) if i not in to_del_index]

    # proactive_policies = v[2]
    # reactive_policies = v[3]
    # all_paths = nx.all_simple_paths(network.topology, source=current_path[0], target=current_path[-1])
    # sorted_paths = sorted(all_paths, cmp=lambda x,y:len(x)-len(y))
    # all_ft_links = set()
    # i = 0
    # while len(all_ft_links) < (len(current_path)-1) and i < len(sorted_paths):
    #   path = sorted_paths[i]
    #   i = i + 1
    #   if path != current_path:
    #       ft_links = compute_ft_links(path, current_path)
    #       if ft_links != []:
    #           l = len(all_ft_links)
    #           all_ft_links.update(ft_links)
    #           if l != len(all_ft_links):
    #               pass

    # if len(all_ft_links) != (len(current_path)-1):
    #   raise Exception("not possible!")

    # break
