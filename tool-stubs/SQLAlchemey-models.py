from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Package(Base):
	__tablename__ = 'package'
	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	download_url = Column(String)
	home_page = Column(String)
	description = Column(String)
	license = Column(String)
	summary = Column(String)
	platform = Column(String)
	
class Release(Base):
	__tablename__ = 'release'
	id = Column(Integer, primary_key=True)
	version = Column(String)
	current = Column(Boolean) # Is this the current version of this package?
	is_url = Column(Boolean) # Does this release also exist in the package['urls'] section?
	upload_time = Column(DateTime)
	python_version = Column(String)
	comment_text = Column(String)
	has_sig = Column(Boolean)
	filename = Column(String)
	packagetype = Column(String)
	size = Column(Integer)
	downloads = Column(Integer)
	package_id = Column(Integer, ForeignKey(Package.id))
	package = relationship(Package, backref=backref('releases'))

class Classifier(Base):
	__tablename__ = 'classifier'
	id = Column(Integer, primary_key=True)
	classifier = Column(String)
	package_id = Column(Integer, ForeignKey(Package.id))
	package = relationship(Package, backref=backref('classifiers'))

class Author(Base):
	__tablename__ = 'author'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	email = Column(String)
	package_id = Column(Integer, ForeignKey(Package.id))
	package = relationship(Package)

class Requirement(Base)
        __tablename__ = 'requirement'
        id = Column(Integer, primary_key=True)
        requirement = Column(String)
        release_id = Column(Integer, ForeignKey(Release.id))
        package = relationship(Release, backref=backref('requirements'))
