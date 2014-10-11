from ap import db
from sqlalchemy import func

def top_classifiers(s, limit=0):
	"""Returns a list of classifiers sorted by how many times they are used (by default limit is none.)"""
	classifiers = s.query(db.Classifier.classifier, func.count(db.Classifier.classifier)).group_by(db.Classifier.classifier).having(func.count(db.Classifier.classifier) > 1).all()
	classifiers.sort(key=lambda tup: tup[1], reverse=True)
	if limit > 0:
		return classifiers[:limit]
	else:
		# this is a lot!
		return classifiers