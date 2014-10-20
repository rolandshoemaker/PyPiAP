from ap import db
from sqlalchemy import func

def top_authors(s, limit=0):
	"""Returns a list of authors sorted by how many packages they have contributed to the index (by default limit is none.)"""
	authors = s.query(db.Author.name, func.count(db.Author.name)).group_by(db.Author.name).having(func.count(db.Author.name) > 1).all()
	authors.sort(key=lambda tup: tup[1], reverse=True)
	if limit > 0:
		return authors[:limit]
	else:
		# this is a lot!
		return authors

def unique_authors(s):
	"""Return number of authors who have only released one package."""
	return s.query(db.Author.name).distinct().count()

def email_tld(tld, s):
	"""Return number of emails using '.tld'."""
	return s.query(db.Author.email).filter(db.Author.email.endswith('.'+tld)).count()

def multiple_authors(s):
	"""Return number of packages that (seem to) have multiple authors."""
	return s.query(db.Author.name).filter(func.lower(db.Author.name).contains('inc').__ne__(True)).filter(func.lower(db.Author.name).contains('ltd').__ne__(True)).filter(db.Author.name.contains(',')).count()

	