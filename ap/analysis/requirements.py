from ap import db
from sqlalchemy import func
import networkx as nx
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_nodelist(s):
	"""Return node list for current Package requirement graph."""
	return [p[0] for p in s.query(db.Package.id).all()]

def get_edgelist(s):
	"""Return edge list for current Package requirement graph."""
	return s.query(db.Package.id, db.Requirement.requirement_id).join(db.Release).filter(db.Release.id==db.Requirement.release_id).filter(db.Release.current==True).filter(db.Requirement.requirement_id.__ne__(None)).all()

def degree_distribution_chart(s, filename):
	"""Create a degree distribution chart."""
	g = nx.DiGraph()
	g.add_nodes_from(get_nodelist(s))
	g.add_edges_from(get_edgelist(s))
	deg_seq = sorted(nx.degree(g).values(), reverse=True)
	plt.hist(deg_seq, bins=range(0, 20, 1), normed=True)
	plt.xticks(range(0, 20, 1))
	plt.title('Requirement graph degree distribution chart')
	plt.xlabel('Degree')
	plt.ylabel('Frequency')
	plt.savefig(filename)
	plt.close()

def in_degree_distribution_chart(s, filename):
	"""Create a in degree distribution chart."""
	g = nx.DiGraph()
	g.add_nodes_from(get_nodelist(s))
	g.add_edges_from(get_edgelist(s))
	deg_seq = sorted(g.in_degree().values(), reverse=True)
	plt.hist(deg_seq, bins=range(0, 20, 1), normed=True)
	plt.xticks(range(0, 20, 1))
	plt.title('Requirement graph indegree distribution chart')
	plt.xlabel('Indegree')
	plt.ylabel('Frequency')
	plt.savefig(filename)
	plt.close()

def out_degree_distribution_chart(s, filename):
	"""Create a in degree distribution chart."""
	g = nx.DiGraph()
	g.add_nodes_from(get_nodelist(s))
	g.add_edges_from(get_edgelist(s))
	deg_seq = sorted(g.out_degree().values(), reverse=True)
	plt.hist(deg_seq, bins=range(0, 20, 1), normed=True)
	plt.xticks(range(0, 20, 1))
	plt.title('Requirement graph outdegree distribution chart')
	plt.xlabel('Outdegree')
	plt.ylabel('Frequency')
	plt.savefig(filename)
	plt.close()

def tuplelist_to_csv(edgelist, filename):
	"""Write list(/list of tuples) to CSV for import into something like Gephi."""
	with open(filename, 'w') as out:
		csv_out = csv.writer(out)
		for row in edgelist:
			csv_out.writerow(row)
