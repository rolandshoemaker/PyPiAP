from ap import db
from sqlalchemy import func

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
	downloads = s.query(func.sum(db.Release.downloads), func.sum(db.Package.downloads_day), func.sum(db.Package.downloads_week), func.sum(db.Package.downloads_month)).first()
	return {'all_time_total': downloads[0],
	    'last_day': downloads[1],
	    'last_week': downloads[2],
	    'last_month': downloads[3]}
