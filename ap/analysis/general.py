from ap import db
from ap.analysis.common import get_pkg_edgelist
from sqlalchemy import func
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re
from urllib.parse import urlparse
from collections import Counter

def pkg_num(s):
	"""Return total number of packages that actually exist on the index."""
	return s.query(db.Packages).count()

def no_releases(s):
	"""Return total number of packages that have no release."""
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
	"""Create chart of the number of downloads per package vs. the number of times it is required, and return this data as a dict."""
	g = nx.DiGraph(get_pkg_edgelist(s))
	plot_data = []
	for n in g.nodes():
		plot_data.append([g.in_degree(n), s.query(func.sum(db.Release.downloads)).filter(db.Release.current==True).filter(db.Release.package_id==n).first()[0]])
	y, x = zip(*plot_data)
	plt.loglog(x, y, marker=',', linestyle='None')
	plt.title('Downloads vs. # times required')
	plt.ylabel('# times required')
	plt.xlabel('Downloads')
	plt.ylim([0, 1000])
	#plt.xlim([0, max(i for i in x if i is not None)+25])
	plt.grid(True)
	plt.savefig(filename)
	plt.close()
	return plot_data

def top_required_packages(s, top=5):
	"""Return list of top required packages and the number of times they are required."""
	g = nx.DiGraph(get_pkg_edgelist(s))
	indegs = list(g.in_degree().items())
	indegs.sort(key=lambda tup: tup[1], reverse=True)
	named_top = []
	for t in indegs[:top]:
		named_top.append([s.query(db.Package).filter(db.Package.id==t[0]).first(), t[1]])
	return named_top

def find_named_ecosystems(s, cutoff=5):
	"""Return dict of named ecosystems and their sizes (split by . and - seperators.)"""
	g = nx.DiGraph(get_pkg_edgelist(s))
	# Consider something worthy of searching if its indegree is more or equal to cutoff
	indegs = [i for i in g.in_degree().items() if i[1] >= cutoff]
	search_names = []
	for t in indegs:
		split_char = ''
		pkg_name = s.query(db.Package.name).filter(db.Package.id==t[0]).first()[0]
		split_search = re.search('\w+([.-])', pkg_name)
		if split_search and len(split_search.groups()) == 1:
			split_char = split_search.group(1)
			if not pkg_name.split(split_char)[0] in search_names:
				search_names.append(pkg_name.split(split_char)[0])
	def name_searcher(sep_char, search_names):
		returner = []
		for n in search_names:
			name_count = s.query(db.Package.name).filter(db.Package.name.startswith(n+sep_char)).count()
			returner.append([n, name_count])
		returner.sort(key=lambda tup: tup[1], reverse=True)
		returner = [r for r in returner if r[1] > 0]
		return returner
	# dot/dash search
	return {'dot-ecosystems': name_searcher('.', search_names), 'dash-ecosystems': name_searcher('-', search_names)}

def home_page_domains(s, cutoff=5):
	urls = [u[0] for u in s.query(db.Package.home_page).all() if u[0]]
	for i, u in enumerate(urls):
		parsed = urlparse(u)
		if parsed.netloc:
			urls[i] = parsed.netloc.lower()
	results = [c for c in Counter(urls).items() if c[1] >= cutoff]
	results.sort(key=lambda tup: tup[1], reverse=True)
	return results
