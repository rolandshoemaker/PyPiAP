from ap import db
from ap.analysis.requirements import get_edgelist
from sqlalchemy import func
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def pkg_num(s):
	"""Return total number of packages that actually exist on the index."""
	return s.query(db.Packages).count()

def no_releases(s):
	"""Return total number of packages that have no releases."""
	# probably better way of doing this?
	return s.query(db.Packages).count() - s.query(db.Package).filter(db.Package.releases.any()).count()

def no_urls(s):
	"""Return total number of packages that have no urls."""
	pass

def downloads(s):
	"""Return dict containing download statistics for the index."""
	downloads = s.query(func.sum(db.Release.downloads), func.sum(db.Release.downloads).filter(db.Release.current==True), func.sum(db.Package.downloads_day), func.sum(db.Package.downloads_week), func.sum(db.Package.downloads_month)).first()
	return {'all_time_total': downloads[0],
		'current_total': downloads[1],
	    'last_day': downloads[2],
	    'last_week': downloads[3],
	    'last_month': downloads[4]}

def downloads_vs_indegree(s, filename):
	g = nx.DiGraph(get_edgelist(s))
	plot_data = []
	for n in g.nodes():
		plot_data.append([s.query(func.sum(db.Release.downloads)).filter(db.Release.current==True).filter(db.Release.package_id==n).first(), g.in_degree(n)])
	plot_data.sort(key=lambda tup: tup[1])
	x, y = zip(*plot_data)
	plt.scatter(x, y, marker=".")
	plt.title('Downloads vs. In Degree')
	plt.ylabel('In Degree')
	plt.xlabel('Downloads')
	plt.savefig(filename)
	plt.close()

def top_required_packages(s, top=5):
	g = nx.DiGraph(get_edgelist(s))
	indegs = list(g.in_degree().items())
	indegs.sort(key=lambda tup: tup[1], reverse=True)
	named_top = []
	for i, t in enumerate(indegs[:top]):
		named_top.append(s.query(db.Package).filter(db.Package.id==t[0]).first())
	return named_top
