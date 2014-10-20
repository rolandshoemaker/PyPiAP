from ap import db
from sqlalchemy import func
import networkx as nx
import pickle

def create_graph(nodelist, edgelist, directed=True):
	"""Build and reutrn a NetworkX graph."""
	if directed:
		g = nx.DiGraph()
	else:
		g = nx.Graph()
	g.add_nodes_from(nodelist)
	g.add_edges_from(edgelist)
	return g

def get_pkg_nodelist(s):
	"""Return node list for current Package requirement graph."""
	return [p[0] for p in s.query(db.Package.id).all()]

def get_pkg_edgelist(s):
	"""Return edge list for current Package requirement graph."""
	return s.query(db.Package.id, db.Requirement.requirement_id).join(db.Release).filter(db.Release.id==db.Requirement.release_id).filter(db.Release.current==True).filter(db.Requirement.requirement_id.__ne__(None)).all()

def tuplelist_to_csv(edgelist, filename):
	"""Write list(/list of tuples) to CSV for import into something like Gephi."""
	with open(filename, 'w') as out:
		csv_out = csv.writer(out)
		for row in edgelist:
			csv_out.writerow(row)

def graph_to_gexf(g, path):
	"""Write a NetworkX graph to a GEXF format file."""
	nx.write_gexf(g, path)

def graph_to_pickle(g):
	"""Return a NetworkX graph as a binary Python Pickle."""
	return pickle.dumps(g, pickle.HIGHEST_PROTOCOL)

def pickle_to_graph(pickle):
	"""Return NetworkX graph from a Pickle."""
	return pickle.loads(pickle)