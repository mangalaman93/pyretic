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
import networkx as nx
import warnings as wn

# Assumptions #
# *assume only one link fails at a time, we don't optimize for multiple link
#   failures at a time as of now
# *assume that all the flows given by the user are independent of each other
#   while calling addft function (in each call to addft)

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
            # iterating over all flow and corresponding handlers in the table
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
                            # now we have the current path and topology, we
                            #  compute back up paths and then install some of
                            #  them. we also store them along with the rest
                            #  the entries which we install after a link failure
                            self.compute_backup_path(current_path)
                            #! continue here (make sure all tules are installed)
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
                    print "link {} has failed".format(failed_link)
                    #! install reactive flow tables entries
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
            flag = true
            for link in link_path:
                if link == clink or link == clink[::-1]:
                    flag = false
                    break
            if flag:
                result.append(clink)
        return result

    def find_covering_paths(self, current_path):
        total_link_count = len(current_path) - 1
        optimal_path_count = self.compute_optimal_path_count(current_path)
        total_tried_paths = 0
        may_be_more_paths = False

        ft_links = set()
        path_list = []
        pathg = nx.all_simple_paths(self.last_topology, source=current_path[0], target=current_path[-1])
        for path in pathg:
            if len(ft_links) == total_link_count:
                break
            if len(ft_links) > total_link_count:
                raise Exception("NOT POSSIBLE")

            old_length = len(ft_links)
            flinks = self.compute_ft_links(path, current_path)
            ft_links.update(flinks)
            if len(ft_links) != old_length:
                path_list.append((path, flinks))

            total_tried_paths = total_tried_paths + 1
            if total_tried_paths == optimal_path_count:
                may_be_more_paths = True;
                break;

        # finding paths by simulating link failures
        if len(ft_links) < total_link_count and may_be_more_paths:
            all_links = [(current_path[i], current_path[i+1]) if current_path[i]<current_path[i+1] \
                else (current_path[i+1], current_path[i]) for i in range(len(current_path)-1)]
            all_links.difference_update(ft_links)
            for link in all_links:
                graph = self.last_topology
                graph.remove_edge(link)
                new_path = nx.shortest_path(graph, current_path[0], current_path[1])
                path_list.append((new_path, self.compute_ft_links(new_path, current_path)))

        if len(ft_links) < total_link_count:
            wn.warn("All links in the path {} cannot be made fault tolerant".format(current_path))

        # removing redundant links
        ft_links = set()
        path_list_copy = []
        for (path, links) in reversed(path_list):
            old_length = len(ft_links)
            ft_links.update(links)
            if len(ft_links) != old_length:
                path_list_copy.append(path)

        return path_list_copy

    # Three optimization goals:
    #  *minimum conflicting rules so that we have to install minimum rules after
    #    a link fails
    #  *minimum total number of rules which are installed to make paths fault tolerant
    #  *backup paths should be as short as possible
    def compute_backup_path(self, current_path):
        proactive_policies = dict()
        reactive_policies = dict()

        # finding all paths covering all the links in the path
        print self.find_covering_paths(current_path)

    def compute_optimal_path_count(self, current_path):
        print "hello"
