from ap import db
from sqlalchemy import func

def top_authors(s, limit=0):
	""""""
	authors = s.query(db.Author.name, func.count(db.Author.name)).group_by(db.Author.name).having(func.count(db.Author.name) > 1).all()
	authors.sort(key=lambda tup: tup[1], reverse=True)
	if limit > 0:
		return authors[:limit]
	else:
		return authors

def unique_authors(s):
	"""Return number of authors who have only released one package."""
	return s.query(db.Author.name).distinct().count()
