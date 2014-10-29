from ap import db
from ap.analysis.common import create_graph, get_pkg_edgelist, get_pkg_nodelist
from sqlalchemy import func
import networkx as nx
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def strong_weak_package_connections(s, g=None):
	if not g:
		g = create_graph(get_pkg_nodelist(s), get_pkg_edgelist(s))
	strong = [t for t in list(nx.strongly_connected_components(g)) if len(t) > 1]
	strong_names = []
	for c in strong:
		names = []
		for p in c:
			names.append(s.query(db.Package.name).filter(db.Package.id==p).first())
		strong_names.append(names)
	weak = [t for t in list(nx.weakly_connected_components(g)) if len(t) > 1]
	weak_names = []
	for c in weak:
		names = []
		for p in c:
			names.append(s.query(db.Package.name).filter(db.Package.id==p).first())
		weak_names.append(names)
	return {'strong': strong_names, 'weak': weak_names}

def packages_with_selfloops(s, g=None):
	"""Return a list of Packages which require themselves."""
	if not g:
		g = create_graph(get_pkg_nodelist(s), get_pkg_edgelist(s))
	id_list = g.nodes_with_selfloops()
	names = []
	for i in id_list:
		names.append(s.query(db.Package.name).filter(db.Package.id==i).first())
	return names

def package_degree_distribution_chart(s, filename, g=None):
	"""Create a degree distribution chart."""
	if not g:
		g = create_graph(get_pkg_nodelist(s), get_pkg_edgelist(s))
	deg_seq = sorted(nx.degree(g).values(), reverse=True)
	plt.hist(deg_seq, bins=range(0, 20, 1), normed=True)
	plt.xticks(range(0, 20, 1))
	plt.title('Requirement graph degree distribution chart')
	plt.xlabel('Degree')
	plt.ylabel('Frequency')
	plt.savefig(filename)
	plt.close()

def package_in_degree_distribution_chart(s, filename, g=None):
	"""Create a in degree distribution chart."""
	if not g:
		g = create_graph(get_pkg_nodelist(s), get_pkg_edgelist(s))
	deg_seq = sorted(g.in_degree().values(), reverse=True)
	plt.hist(deg_seq, bins=range(0, 20, 1), normed=True)
	plt.xticks(range(0, 20, 1))
	plt.title('Requirement graph indegree distribution chart')
	plt.xlabel('Indegree')
	plt.ylabel('Frequency')
	plt.savefig(filename)
	plt.close()

def package_out_degree_distribution_chart(s, filename, g=None):
	"""Create a in degree distribution chart."""
	if not g:
		g = create_graph(get_pkg_nodelist(s), get_pkg_edgelist(s))
	deg_seq = sorted(g.out_degree().values(), reverse=True)
	plt.hist(deg_seq, bins=range(0, 20, 1), normed=True)
	plt.xticks(range(0, 20, 1))
	plt.title('Requirement graph outdegree distribution chart')
	plt.xlabel('Outdegree')
	plt.ylabel('Frequency')
	plt.savefig(filename)
	plt.close()
