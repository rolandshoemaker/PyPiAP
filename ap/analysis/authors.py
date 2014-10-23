from ap import db
from sqlalchemy import func
import re, itertools
from collections import Counter

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

def author_email_domains(s, cutoff=2):
	domains = [d[0].split('@')[-1].lower().replace('>', '') for d in s.query(db.Author.email).distinct().all() if d[0] and re.match(r'[^@]+@[^@]+\.[^@]+', d[0])]
	results = [c for c in Counter(domains).items() if c[1] >= cutoff]
	results.sort(key=lambda tup: tup[1], reverse=True)
	return results
