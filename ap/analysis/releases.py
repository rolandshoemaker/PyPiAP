from ap import db
from sqlalchemy import func
import datetime, numpy

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
	"""Return the average interval between releases."""
	# Note this takes forever to run, probably could find a better way?
	# oct 11 - this should be somewhat faster?
	pkgs = s.query(db.Package).filter(db.Package.releases.any()).all()
	time_dlts = []
	for p in pkgs:
		if len(p.releases) > 1:
			p.releases.sort(key=lambda tup: tup.upload_time, reverse=True)
			times = [p.releases[i].upload_time-p.releases[i+1].upload_time for i in range(len(p.releases)-2)]
			time_dlts.append(numpy.mean(times))
	return numpy.mean(time_dlts)

def avg_release_age(s):
	"""Return average age of current releases as a datetime.timedelta object."""
	# should remove outliers and all that silly stuff
	releases = [datetime.datetime.now() - r[0] for r in s.query(db.Release.upload_time).filter(db.Release.current==True).all()]
	return numpy.mean(releases)
