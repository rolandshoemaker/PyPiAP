from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import datetime
from time import strptime

import config

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
	downloads_month = Column(Integer)
	downloads_week = Column(Integer)
	downloads_day = Column(Integer)
	
class Release(Base):
	__tablename__ = 'release'
	id = Column(Integer, primary_key=True)
	version = Column(String)
	current = Column(Boolean) # Is this the current version of this package?
	is_url = Column(Boolean) # Does this release also exist in package['urls']?
	upload_time = Column(DateTime)
	python_version = Column(String)
	comment_text = Column(String)
	has_sig = Column(Boolean)
	filename = Column(String)
	packagetype = Column(String)
	size = Column(Integer)
	downloads = Column(Integer)
	package_id = Column(Integer, ForeignKey(Package.id))
	package = relationship(Package, backref=backref('releases', cascade='all, delete-orphan'))

class Classifier(Base):
	__tablename__ = 'classifier'
	id = Column(Integer, primary_key=True)
	classifier = Column(String)
	package_id = Column(Integer, ForeignKey(Package.id))
	package = relationship(Package, backref=backref('classifiers', cascade='all, delete-orphan'))

class Author(Base):
	__tablename__ = 'author'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	email = Column(String)
	package_id = Column(Integer, ForeignKey(Package.id))
	package = relationship(Package, backref=backref('author', cascade='all, delete-orphan'))

class Requirement(Base):
        __tablename__ = 'requirement'
        id = Column(Integer, primary_key=True)
        version = Column(String)
        op = Column(String)
        requirement_id = Column(Integer, ForeignKey(Package.id))
        package = relationship(Package)
        release_id = Column(Integer, ForeignKey(Release.id))
        release = relationship(Release, backref=backref('requirements', cascade='all, delete-orphan'))

engine = create_engine(config.db)
Base.metadata.create_all(engine)

def insert_new(info, s):
    package = Package(name=info['info']['name'],
        download_url=info['info']['download_url'],
        home_page=info['info']['home_page'],
        description=info['info']['description'],
        license=info['info']['license'],
        summary=info['info']['summary'],
        platform=info['info']['platform'],
        downloads_month=info['info']['downloads']['last_month'],
        downloads_week=info['info']['downloads']['last_week'],
        downloads_day=info['info']['downloads']['last_day'])
    s.add(package)
    author = Author(name=info['info']['author'],
        email=info['info']['author_email'],
        package=package)
    s.add(author)
    for c in info['info']['classifiers']:
        classifier = Classifier(classifier=c, package=package)
        s.add(classifier)
    for version, pkgs in info['releases'].items():
        for i, p in enumerate(pkgs):
            is_url = p in info['urls']
            current = version == info['info']['version']
            release = Release(version=version,
                current=current,
                is_url=is_url,
                upload_time=datetime.datetime(*strptime(info['releases'][version][i]['upload_time'], '%Y-%m-%dT%H:%M:%S')[:6]),
                python_version=info['releases'][version][i]['python_version'],
                comment_text=info['releases'][version][i]['comment_text'],
                has_sig=info['releases'][version][i]['has_sig'],
                filename=info['releases'][version][i]['filename'],
                packagetype=info['releases'][version][i]['packagetype'],
                size=info['releases'][version][i]['size'],
                downloads=info['releases'][version][i]['downloads'],
                package=package)
            s.add(release)
    s.commit()
    print('[sql:insert] inserted records for '+package.name)

def new_requirements(info, s):
    for version, pkgs in info['releases'].items():
        for i, p in enumerate(pkgs):
            if info['releases'][version][i]['packagetype'] == 'sdist': # and info['releases'][version][i] in info['urls']:
                compressed_path = '/pypi_mirror/web/' + '/'.join(info['releases'][version][i]['url'].split('/')[3:])
                for r in extract_requirements(compressed_path, info['info']['name']):
                    try:
                        req_info = req_parser.parse(r)
                        if req_info.project_name == "":
                            continue
                        req_pkg_name = req_info.project_name
                        if len(req_info.specs) > 0:
                            req_op = req_info.specs[0][0]
                            req_version = req_info.specs[0][1]
                        else:
                            req_op = ''
                            req_version = ''
                        req = Requirement(version=req_version,
                            op=req_op,
                            package=s.query(Package).filter(Package.name==req_pkg_name).first(),
                            release=s.query(Release).filter(Release.filename==info['releases'][version][i]['url'].split('/')[-1]).first())
                        s.add(req)
                        s.commit()
                    except ValueError:
                        pass
    print('[sql:insert] inserted requirements for '+info['info']['name'])

def update_requirements(info, s):
	pass

def update_old(info, s):
    print('[sql:update] updated records for '+package.name)
    pass

def remove_dead(pkg_name, s):
    package = s.query(Package).filter(Package.name==pkg_name).first()
    s.delete(package)
    print('[sql:delete] removed records for '+pkg_name)
    s.commit()