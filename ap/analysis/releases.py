from ap import db
from sqlalchemy import func

def num(s):
	"""Return total number of releases."""
	return s.query(db.Release).count()

def current_num(s):
	"""Return number of current releases."""
	return s.query(db.Release).filter(db.Release.current==True).count()

def total_size(s):
	"""Return sum of all release sizes."""
	return s.query(func.sum(db.Release)).scalar()

def current_size(s):
	"""Return sum of all current release sizes."""
	return s.query(func.sum(db.Release)).filter(db.Release.current==True).scalar()

def avg_size(s):
	"""Return average size of releases."""
	return s.query(func.avg(db.Release.size)).scalar()
