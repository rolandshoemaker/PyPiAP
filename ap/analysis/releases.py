from ap import db
from sqlalchemy import func
import datetime

def num(s):
	"""Return total number of releases."""
	return s.query(db.Release).count()

def current_num(s):
	"""Return number of current releases."""
	return s.query(db.Release).filter(db.Release.current==True).count()

def avg_downloads(s):
	"""Return average number of downloads."""
	return s.query(func.avg(db.Release.downloads)).scalar()

def major_version_distribution(s):
	"""Return a dict of how many current releases have a major version in [0-9]."""
	nums = {}
	for n in range(10):
		nums[str(n)] = s.query(db.Release).filter(db.Release.current==True).filter(db.Release.version.startswith(str(n))).count()
	return nums

def total_size(s):
	"""Return sum of all release sizes in bytes."""
	return s.query(func.sum(db.Release.size)).scalar()

def current_size(s):
	"""Return sum of all current release sizes in bytes."""
	return s.query(func.sum(db.Release.size)).filter(db.Release.current==True).scalar()

def avg_size(s):
	"""Return average size of releases in bytes."""
	return s.query(func.avg(db.Release.size)).scalar()

def minmax_size(s):
	"""Return the minimum and maximum release size in bytes as a tuple."""
	return (s.query(func.min(db.Release.size)).scalar(), s.query(func.max(db.Release.size)).scalar())

def avg_release_interval(s):
	avgs = datetime.timedelta()
	pkgs = s.query(db.Package).filter(db.Package.releases.any()).all()
	for p in pkgs:
		if len(p.releases) > 1:
			times = []
			time_dlts = datetime.timedelta()
			for r in p.releases:
				times.append(r.upload_time)
			times.sort(reverse=True)
			for i, t in enumerate(times):
				if len(times) > i+1:
					time_dlts += (t-times[i+1])
			avgs += time_dlts/(len(times)-1)
	return avgs/len(pkgs)