#!/usr/bin/python
import networkx as nx

# example topology
topology = nx.Graph()
# topology.add_edges_from([(2,5), (5,3), (2,6), (6,3)])
# current_path = [2,5,3]

topology.add_edges_from([(1,2), (2,3), (3,4), (4,5), (2,6), (6,4), (1,7), (1,8), (7,8), (4,9), (9,5), (1,6)])
current_path = [7,1,2,3,4,5]

# helper functions
def compute_ft_links(path, current):
	i = 0
	to_del_index = []
	for n1 in path:
		j = 0
		for n2 in current:
			if n1 == n2:
				if i+1<len(path) and (j+1)<len(current) and path[i+1] == current[j+1]:
					to_del_index.append(j)
				if (i-1)>=0 and (j-1)>=0 and path[i-1] == current[j-1]:
					to_del_index.append(j-1)
			j = j+1
		i = i+1
	return [i for j, i in enumerate(current[:-1]) if j not in to_del_index]

# algorithm
all_paths = nx.all_simple_paths(topology, source=current_path[0], target=current_path[-1])
sorted_paths = sorted(all_paths, cmp=lambda x,y:len(x)-len(y))
all_ft_links = set()
used_paths = []
i = 0
while len(all_ft_links) < (len(current_path)-1) and i < len(sorted_paths):
	path = sorted_paths[i]
	i = i + 1
	if path != current_path:
		ft_links = compute_ft_links(path, current_path)
		if ft_links != []:
			all_ft_links.update(ft_links)
			used_paths.append(path)

if len(all_ft_links) < (len(current_path)-1):
	raise Exception("not possible to make all links fault tolerant")

if len(all_ft_links) != (len(current_path)-1):
	raise Exception("not possible!")

print used_paths
