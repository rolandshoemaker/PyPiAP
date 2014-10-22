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

def framework_sizes_by_classifier(s):
	"""Return dict of Frameworks and their size based on how many packages use their framework classifier."""
	framework_trove = ['Framework :: BFG',
		'Framework :: Bob',
		'Framework :: Bottle',
		'Framework :: Buildout',
		'Framework :: Chandler',
		'Framework :: CherryPy',
		'Framework :: CubicWeb',
		'Framework :: Django',
		'Framework :: Flask',
		'Framework :: IDLE',
		'Framework :: IPython',
		'Framework :: Opps',
		'Framework :: Paste',
		'Framework :: Plone',
		'Framework :: Pylons',
		'Framework :: Pyramid',
		'Framework :: Review Board',
		'Framework :: Scrapy',
		'Framework :: Setuptools Plugin',
		'Framework :: Trac',
		'Framework :: Tryton',
		'Framework :: TurboGears',
		'Framework :: Twisted',
		'Framework :: ZODB',
		'Framework :: Zope2',
		'Framework :: Zope3']
	sizes = {}
	for f in framework_trove:
		sizes[f.split(' :: ')[1]] = s.query(db.Classifier.classifier).filter(db.Classifier.classifier==f).count()
	return sizes

def nonpython_pkgs(s):
	"""Return a dict of non-python Language classifiers and how many times they are used."""
	other_classifiers = ['Programming Language :: Ada',
		'Programming Language :: APL',
		'Programming Language :: ASP',
		'Programming Language :: Assembly',
		'Programming Language :: Awk',
		'Programming Language :: Basic',
		'Programming Language :: C',
		'Programming Language :: C#',
		'Programming Language :: C++',
		'Programming Language :: Cold Fusion',
		'Programming Language :: Cython',
		'Programming Language :: Delphi/Kylix',
		'Programming Language :: Dylan',
		'Programming Language :: Eiffel',
		'Programming Language :: Emacs-Lisp',
		'Programming Language :: Erlang',
		'Programming Language :: Euler',
		'Programming Language :: Euphoria',
		'Programming Language :: Forth',
		'Programming Language :: Fortran',
		'Programming Language :: Haskell',
		'Programming Language :: Java',
		'Programming Language :: JavaScript',
		'Programming Language :: Lisp',
		'Programming Language :: Logo',
		'Programming Language :: ML',
		'Programming Language :: Modula',
		'Programming Language :: Objective C',
		'Programming Language :: Object Pascal',
		'Programming Language :: OCaml',
		'Programming Language :: Other',
		'Programming Language :: Other Scripting Engines',
		'Programming Language :: Pascal',
		'Programming Language :: Perl',
		'Programming Language :: PHP',
		'Programming Language :: Pike',
		'Programming Language :: Pliant',
		'Programming Language :: PL/SQL',
		'Programming Language :: PROGRESS',
		'Programming Language :: Prolog',
		'Programming Language :: REBOL',
		'Programming Language :: Rexx',
		'Programming Language :: Ruby',
		'Programming Language :: Scheme',
		'Programming Language :: Simula',
		'Programming Language :: Smalltalk',
		'Programming Language :: SQL',
		'Programming Language :: Tcl',
		'Programming Language :: Unix Shell',
		'Programming Language :: Visual Basic',
		'Programming Language :: XBasic',
		'Programming Language :: YACC',
		'Programming Language :: Zope']
	sizes = {}
	for f in other_classifiers:
		sizes[f.split(' :: ')[1]] = s.query(db.Classifier.classifier).filter(db.Classifier.classifier==f).count()
	return sizes