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

    def addft(self, flow, source, goal):
        if not isinstance(flow, match):
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
        filtered_query = flow >> (matchA + matchB) >> query
        key = (flow, source, goal)
        value = (True, filtered_query, set(), dict())
        self.flow_dict[key] = value
        self.update_policy()

    def update_policy(self):
        new_policy = self.user_policy
        for key,value in self.flow_dict.items():
            # proactive policies
            if value[0]:
                new_policy = new_policy + value[1]
            else:
                new_policy = new_policy + value[2]
            # reactive policies
            for link,pols in value[3].items():
                if link in self.current_failures:
                    new_policy = new_policy + pols
        self.policy = new_policy

    def install_backup_paths(self, pkt):
        with self.lock:
            for key,value in self.flow_dict.items():
                # if back up policy is already not installed
                if value[0]:
                    try:
                        flag = True
                        for x,y in key[0].map.iteritems():
                            flag = flag and (pkt[x] == y)
                    except:
                        flag = False

                    # if pkt corresponds to current flow
                    if flag:
                        current_path = self.compute_current_path(pkt, key[2])
                        if current_path:
                            value = self.compute_backup_path(current_path, key[0])
                            # removing handlers for the packet
                            self.flow_dict[key] = (False, value[1]) + value[2:]
            self.update_policy()

    def set_network(self, network):
        with self.lock:
            if self.ftopology:
                diff_topo = Topology.difference(self.ftopology, network.topology)
                if diff_topo and len(diff_topo.edges()) == 1:
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
                        wn.warn("we don't handle this case as of now")
            self.ftopology = network.topology
            self.update_policy()

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
                next_switch = self.ftopology.node[pkt["switch"]]["ports"][new_pkt["outport"]].linked_to
                in_port = int(str(next_switch).split('[')[1].split(']')[0])
                next_switch = int(str(next_switch).split('[')[0])
                if next_switch is None:
                    return []
                current_path.append(pkt["switch"])
                new_pkt = new_pkt.modify(switch=next_switch)
                new_pkt = new_pkt.modify(inport=in_port)
        except:
            return []
        current_path.append(goal)
        return current_path

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
                if link == clink or link == clink[::-1]:
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
    def compute_backup_path(self, cpath, flow):
        proactive_policies = None
        reactive_policies = {}
        covering_paths = self.find_covering_paths(cpath)

        # conflict detection, populating the data structure
        # conflict => same incoming but different outgoing port
        # data structure: (current switch, incoming switch) -> {outgoing switch: set link}
        rules = {}
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

        # storing rules
        for (cw, iw),d in rules.iteritems():
            inport = 0
            outport = 0
            # conflicts, reactive
            for ow,links in d.items():
                # when current switch is last switch
                if cw == cpath[-2] or not links:
                    continue
                rule = None
                for port,value in self.ftopology.node[cw]['ports'].items():
                    # do not loop for None
                    if value.linked_to:
                        next_switch = int(str(value.linked_to).split('[')[0])
                        if next_switch == ow:
                            outport = port
                        elif next_switch == iw:
                            inport = port
                # when current switch is initial switch
                if iw < 0:
                    if cpath[1] != cw:
                        raise Exception("NOT POSSIBLE")
                    rule = flow >> match(switch=cw) >> fwd(outport)
                else:
                    rule = flow >> match(switch=cw, inport=inport) >> fwd(outport)
                    rule = rule + (flow >> match(switch=cw, inport=outport) >> fwd(inport))

                if len(d) > 1:
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

        (a,b,c,d) = self.flow_dict[(flow, cpath[1], cpath[-2])]
        result = (a, b, proactive_policies, reactive_policies)
        self.flow_dict[(flow, cpath[1], cpath[-2])] = result
        del cpath[0]
        del cpath[-1]
        return result

    #! find a proof for this
    def compute_optimal_path_count(self, current_path):
        n = len(current_path)
        return int(n * log(n))
