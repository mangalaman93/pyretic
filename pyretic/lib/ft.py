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

from math import *
import networkx as nx
import warnings as wn

# Assumptions #
# *assume only one link fails at a time, we don't optimize for multiple
#   link failures at a time as of now
# *assume that all the flows given by the user are independent of each
#   other while calling addft function (in each call to addft)

# Caution #
# *^what about the rules already installed, they should not have
#  incoming node as part of the rules itself
# *handle dynamic policies

# Future work #
#  *ft as part of pyretic to make it more efficient, we know difference
#    but still we have to compute the whole policy and pyretic computes
#    the difference again
#  *better algorithm
#  *no modification support
#  *preferred backup path support
#    *specify list of links not to use as back up paths (global)
#    *specify list of links preferred to use as back up paths (global)

class ft(DynamicPolicy):
    def __init__(self, pol):
        super(ft, self).__init__()
        self.ftopology = None         # stores current topology
        self.flow_dict = {}           # stores everything related to ft
                                      # (flag, flow, proactive, reactive)
        self.user_policy = pol        # stores user policy
        self.current_failures = set() # stores all currently failed links
        self.lock = Lock()
        self.policy = self.user_policy

    def addft(self, inflow, outflow, source, goal):
        if not isinstance(inflow, match):
            raise Exception("unknown flow type in addft function call")
        if not isinstance(outflow, match):
            raise Exception("unknown flow type in addft function call")

        if isinstance(source, int):
            matchA = match(switch=source)
        else:
            raise Exception("unknown node type in addft function call")

        if isinstance(goal, int):
            matchB = match(switch=goal)
        else:
            raise Exception("unknown node type in addft function call")

        # registers call back for installing back up path when first
        #  packet corresponding to flow comes into the network
        query = packets(None)
        query.register_callback(self.install_backup_paths)
        filtered_query = (inflow >> (matchA + matchB) >> query)
        key = ((inflow, outflow), source, goal)
        value = (True, filtered_query, set(), dict())
        self.flow_dict[key] = value
        self.update_policy()

    def update_policy(self):
        new_policy = None
        for key,value in self.flow_dict.items():
            # proactive policies
            if value[0]:
                if new_policy:
                    new_policy = new_policy + value[1]
                else:
                    new_policy = value[1]
            else:
                if new_policy:
                    new_policy = new_policy + value[2]
                else:
                    new_policy = value[2]
            # reactive policies
            for link,pols in value[3].items():
                if link in self.current_failures:
                    if new_policy:
                        new_policy = new_policy + pols
                    else:
                        new_policy = pols
        if new_policy:
            new_policy = new_policy + self.user_policy
        else:
            new_policy = self.user_policy
        self.policy = new_policy

    def install_backup_paths(self, pkt):
        with self.lock:
            for key,value in self.flow_dict.items():
                # if back up policy is already not installed
                if value[0]:
                    try:
                        flag = True
                        (inflow, outflow) = key[0]
                        for x,y in inflow.map.iteritems():
                            flag = flag and (pkt[x] == y)
                    except:
                        flag = False

                    # if pkt corresponds to current flow
                    if flag:
                        current_path = self.compute_current_path(pkt, key[1], key[2])
                        if current_path:
                            value = self.compute_backup_path(current_path, inflow, outflow)
                            # removing handlers for the packet
                            self.flow_dict[key] = (False, value[1]) + value[2:]
            self.update_policy()

    def set_network(self, network):
        with self.lock:
            if self.ftopology:
                diff_topo = Topology.difference(self.ftopology, network.topology)
                if diff_topo and len(diff_topo.edges()) == 1:
                    # if a link has failed
                    failed_link = diff_topo.edges()[0]
                    print "link {} has failed".format(failed_link)
                    if failed_link not in self.current_failures:
                        self.current_failures.update([tuple(sorted(failed_link))])
                else:
                    # if a failed link comes back up
                    diff_topo = Topology.difference(network.topology, self.ftopology)
                    if diff_topo and len(diff_topo.edges()) == 1:
                        up_link = diff_topo.edges()[0]
                        print "link {} has compe up back".format(up_link)
                        if up_link in self.current_failures:
                            self.current_failures.discard(up_link)
                    else:
                        # we just pass the change to the user
                        if isinstance(self.user_policy, DynamicPolicy):
                            old_user_policy = self.user_policy.policy
                            self.user_policy.set_network(network)
                            new_user_policy = self.user_policy.policy
                            if old_user_policy != new_user_policy:
                                # flush entries
                                for key,value in self.flow_dict.items():
                                    self.flow_dict[key] = (True, value[1], set(), dict())
            self.ftopology = network.topology
            self.update_policy()

    # helper functions
    def compute_current_path_helper(self, pkt, goal):
        if pkt["switch"] != goal:
            cpkts = self.user_policy.eval(pkt)
            if len(cpkts) == 0:
                return []
            for packet in cpkts:
                next_switch = self.ftopology.node[pkt["switch"]]["ports"][packet["outport"]].linked_to
                in_port = int(str(next_switch).split('[')[1].split(']')[0])
                next_switch = int(str(next_switch).split('[')[0])
                if next_switch is None:
                    return []
                pkt = pkt.modify(switch=next_switch)
                pkt = pkt.modify(inport=in_port)
                cpath = self.compute_current_path_helper(pkt, goal)
                if cpath:
                    return ([packet["switch"]] + cpath)
                else:
                    return []
        else:
            return [goal]

    def compute_current_path(self, pkt, source, goal):
        # if packet did not come from source but goal
        if pkt['switch'] != source:
            pkt = pkt.modify(switch=source)
        try:
            return self.compute_current_path_helper(pkt, goal)
        except:
            return []

    # with the convention of returning links with smaller node value first
    def compute_ft_links(self, path, current):
        link_path = [(path[i], path[i+1]) if path[i]<path[i+1] \
            else (path[i+1], path[i]) for i in range(len(path)-1)]
        link_current = [(current[i], current[i+1]) if current[i]<current[i+1] \
            else (current[i+1], current[i]) for i in range(len(current)-1)]
        result = []

        for clink in link_current:
            flag = True
            for link in link_path:
                if link == clink:
                    flag = False
                    break
            if flag:
                result.append(clink)
        return result

    def find_covering_paths(self, cpath):
        total_link_count = len(cpath) - 1
        optimal_path_count = self.compute_optimal_path_count(cpath)
        total_tried_paths = 0
        may_be_more_paths = False

        ft_links = set()
        path_list = []
        pathg = nx.all_simple_paths(self.ftopology, source=cpath[0], target=cpath[-1])
        for path in pathg:
            if len(ft_links) == total_link_count:
                break
            if len(ft_links) > total_link_count:
                raise Exception("NOT POSSIBLE")

            old_length = len(ft_links)
            flinks = self.compute_ft_links(path, cpath)
            ft_links.update(flinks)
            if len(ft_links) != old_length:
                path_list.append((path, flinks))

            total_tried_paths = total_tried_paths + 1
            if total_tried_paths == optimal_path_count:
                may_be_more_paths = True;
                break;

        # finding paths by simulating link failures
        if len(ft_links) < total_link_count and may_be_more_paths:
            all_links = [(cpath[i], cpath[i+1]) if cpath[i]<cpath[i+1] \
                else (cpath[i+1], cpath[i]) for i in range(len(cpath)-1)]
            all_links.difference_update(ft_links)
            for link in all_links:
                graph = self.ftopology
                graph.remove_edge(link)
                new_path = nx.shortest_path(graph, cpath[0], cpath[-1])
                path_list.append((new_path, self.compute_ft_links(new_path, cpath)))

        if len(ft_links) < total_link_count:
            wn.warn("All links in {} cannot be made fault tolerant".format(cpath))

        # removing redundant links
        ft_links = set()
        path_list_copy = []
        for (path, links) in reversed(path_list):
            old_length = len(ft_links)
            ft_links.update(links)
            if len(ft_links) != old_length:
                path_list_copy.append((path, links))

        return path_list_copy

    # Three optimization goals:
    #  *minimum conflicting rules so that we have to install minimum rules after
    #    a link fails
    #  *minimum total number of rules which are installed to make paths fault tolerant
    #  *backup paths should be as short as possible
    def compute_backup_path(self, cpath, inflow, outflow):
        proactive_policies = None
        reactive_policies = {}
        covering_paths = self.find_covering_paths(cpath)

        # conflict detection, populating the data structure
        # conflict => same incoming but different outgoing port
        #          => same outgoing but different incoming port (for reverse path)*
        # data structure: (current switch, incoming switch) -> {outgoing switch: set link}
        #               : (current switch, outgoing switch) -> {incoming switch}
        # we keep another dictionary to make sure that the conflict* do not exist
        #  for reverse path
        rules = {}
        rules_rev = {}
        covering_paths.insert(0, (cpath, []))
        for (path, links) in covering_paths:
            # -1 > A & -2 > B (end hosts)
            path.insert(0, -1)
            path.append(-2)
            for i in range(1, len(path)-1):
                if (path[i], path[i-1]) in rules:
                    if path[i+1] in rules[path[i], path[i-1]]:
                        rules[path[i], path[i-1]][path[i+1]].update(links)
                    else:
                        rules[path[i], path[i-1]][path[i+1]] = set(links)
                else:
                    rules[path[i], path[i-1]]= {path[i+1]: set(links)}

                if (path[i], path[i+1]) in rules_rev:
                    rules_rev[path[i], path[i+1]].update([path[i-1]])
                else:
                    rules_rev[path[i], path[i+1]]= set([path[i-1]])

        # storing rules
        for (cw, iw),d in rules.iteritems():
            inport = 0
            outport = 0
            for ow,links in d.items():
                # when current switch is last switch
                if not links:
                    continue
                # otherwise calculating inport and outport
                if iw > 0 or ow > 0:
                    for port,value in self.ftopology.node[cw]['ports'].items():
                        # do not loop for None
                        if value.linked_to:
                            next_switch = int(str(value.linked_to).split('[')[0])
                            if next_switch == ow:
                                outport = port
                            elif next_switch == iw:
                                inport = port

                #! ONLY FOR DEMO PURPOSES (find another solution)
                if outport == 0 and ow < 0:
                    for port,value in self.ftopology.node[cw]['ports'].items():
                        # do not loop for None
                        if not value.linked_to:
                            outport = port

                if inport == 0 and iw < 0:
                    for port,value in self.ftopology.node[cw]['ports'].items():
                        # do not loop for None
                        if not value.linked_to:
                            inport = port

                # when current switch is initial switch
                if iw < 0:
                    if cpath[1] != cw:
                        raise Exception("NOT POSSIBLE")
                    rule = inflow >> match(switch=cw) >> fwd(outport)
                    rule = rule + (outflow >> match(switch=cw) >> fwd(inport))
                elif ow < 0:
                    rule = outflow >> (match(switch=cw)) >> fwd(inport)
                    rule = rule + (inflow >> match(switch=cw) >> fwd(outport))
                else:
                    rule = inflow >> match(switch=cw, inport=inport) >> fwd(outport)
                    rule = rule + (outflow >> match(switch=cw, inport=outport) >> fwd(inport))

                if len(d) > 1 or len(rules_rev[cw, ow]) > 1:
                    # conflicts, reactive
                    for link in links:
                        if link in reactive_policies:
                            reactive_policies[link] = reactive_policies[link] + rule
                        else:
                            reactive_policies[link] = rule
                else:
                    # no conflicts, proactive
                    if proactive_policies:
                        proactive_policies = proactive_policies + rule
                    else:
                        proactive_policies = rule

        (a,b,c,d) = self.flow_dict[((inflow, outflow), cpath[1], cpath[-2])]
        result = (a, b, proactive_policies, reactive_policies)
        self.flow_dict[((inflow, outflow), cpath[1], cpath[-2])] = result
        return result

    # proof: http://en.wikipedia.org/wiki/Coupon_collector's_problem
    # maximizing the probability of collecting all the links
    def compute_optimal_path_count(self, current_path):
        n = len(current_path)
        return int(n * log(n))
