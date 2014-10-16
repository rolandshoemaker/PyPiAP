from ap import db
from sqlalchemy import func
import networkx as nx
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_edgelist(s, names=False):
	"""Return edgelist for current Package requirement graph."""
	return s.query(db.Package.id, db.Requirement.requirement_id).join(db.Release).filter(db.Release.id==db.Requirement.release_id).filter(db.Release.current==True).filter(db.Requirement.requirement_id.__ne__(None)).all()

def degree_rank_chart(edgelist, filename):
	"""Create a degree rank chart."""
	g = nx.DiGraph(edgelist)
	deg_seq = sorted(nx.degree(g).values(), reverse=True)
	plt.loglog(deg_seq, 'b-')
	plt.title('Degree rank chart')
	plt.ylabel('degree')
	plt.xlabel('rank')
	plt.savefig(filename)
	plt.close()

def tuplelist_to_csv(edgelist, filename):
	"""Write list(/list of tuples) to CSV for import into something like Gephi."""
	with open(filename, 'w') as out:
		csv_out = csv.writer(out)
		for row in edgelist:
			csv_out.writerow(row)
