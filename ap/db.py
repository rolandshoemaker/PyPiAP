from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Interval, TIMESTAMP, PickleType, LargeBinary
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, update, func
from sqlalchemy.orm import sessionmaker, scoped_session
import datetime
from time import strptime

from ap import config
from ap.utils import peeper

# JSON decomp tables
json_Base = declarative_base()

class Package(json_Base):
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
	
class Release(json_Base):
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

class Classifier(json_Base):
	__tablename__ = 'classifier'
	id = Column(Integer, primary_key=True)
	classifier = Column(String)
	package_id = Column(Integer, ForeignKey(Package.id))
	package = relationship(Package, backref=backref('classifiers', cascade='all, delete-orphan'))

class Author(json_Base):
	__tablename__ = 'author'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	email = Column(String)
	package_id = Column(Integer, ForeignKey(Package.id))
	package = relationship(Package, backref=backref('author', cascade='all, delete-orphan'))

class Requirement(json_Base):
    __tablename__ = 'requirement'
    id = Column(Integer, primary_key=True)
    version = Column(String)
    op = Column(String)
    requirement_id = Column(Integer, ForeignKey(Package.id))
    package = relationship(Package)
    release_id = Column(Integer, ForeignKey(Release.id))
    release = relationship(Release, backref=backref('requirements', cascade='all, delete-orphan'))

# Statistic collection tables
stats_Base = declarative_base()

class Build(stats_Base):
    __tablename__ = 'builds'
    id = Column(Integer, primary_key=True)
    build_timestamp = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    rebuild_duration = Column(Interval)
    analysis_duration = Column(Interval)
    index_count = Column(Integer)
    real_count = Column(Integer)
    phantom_count = Column(Integer)
    json_size = Column(Integer)
    mirror_size = Column(Integer)
    database_size = Column(Integer)
    packages_inserted = Column(Integer)
    packages_updated = Column(Integer)
    packages_removed = Column(Integer)

class Analysis(stats_Base):
    __tablename__ = 'general'
    id = Column(Integer, primary_key=True)
    build_id = Column(Integer, ForeignKey(Build.id))
    build = relationship(Build, backref=backref('general', cascase='all, delete-orphan'))
    # General
    no_releases = Column(Integer)
    no_url = Column(Integer)
    total_downloads = Column(Integer)
    total_current_downloads = Column(Integer)
    downloads_last_day = Column(Integer)
    downloads_last_week = Column(Integer)
    downloads_last_month = Column(Integer)
    top_required_packages = Column(PickleType)
    named_ecosystems = Column(PickleType)
    home_page_domains = Column(PickleType)
    # Authors
    top_authors = Column(PickleType)
    unique_authors = Column(Integer)
    multiple_authors = Column(Integer)
    author_email_domains = Column(PickleType)
    # Classifiers
    top_classifiers = Column(PickleType)
    framework_sizes_by_classifier = Column(PickleType)
    nonpython_pkgs = Column(PickleType)
    natural_language_distribution = Column(PickleType)
    # Releases
    total_releases = Column(Integer)
    current_releases = Column(Integer)
    average_download_per_release = Column(Integer)
    major_version_distribution = Column(PickleType)
    all_releases_size = Column(Integer)
    current_releases_size = Column(Integer)
    average_release_size = Column(Integer)
    average_release_interval = Column(Interval)
    average_release_age = Column(Interval)
    # Requirements
    strong_weak_package_connections = Column(PickleType)
    packages_with_selfloops = Column(PickleType)
    # Graphs
    package_requirement_graph = Column(LargeBinary)
    package_author_graph = Column(LargeBinary)

json_engine = create_engine(config.db+'pypi-json')
stats_engine = create_engine(config.db+'pypi-stats')
json_Base.metadata.create_all(json_engine)
stats_Base.metadata.create_all(stats_engine)

def make_session(engine, autoflush=True, autocommit=False, scoped=False):
    if not scoped:
	    session = sessionmaker()
	    session.configure(autoflush=autoflush, autocommit=autocommit, bind=engine)
    else:
        session = scoped_session(sessionmaker())
        session.configure(autoflush=autoflush, autocommit=autocommit, bind=engine)
    return session()

def insert_new(info, s):
    """Add a new set of records based on json."""
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
    print('[sql:insert] inserted records for '+package.name)

def new_requirements(info, s):
    """Insert new set of requirement records for a package, should be done after full package index is built."""
    for version, pkgs in info['releases'].items():
        for i, p in enumerate(pkgs):
            if info['releases'][version][i]['packagetype'] == 'sdist': # and info['releases'][version][i] in info['urls']:
                compressed_path = '/pypi_mirror/web/' + '/'.join(info['releases'][version][i]['url'].split('/')[3:])
                for r in peeper.extract_requirements(compressed_path, info['info']['name']):
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
                    except ValueError:
                        pass
    print('[sql:insert] inserted requirements for '+info['info']['name'])

def update_requirements(info, s):
	# since we are just nuking requirements lets just pass this through now
	new_requirements(info, s)

def update_old(info, s):
    package = s.query(Package).where(Package.name==info['info']['name']).first()
    package.name = info['info']['name']
    package.download_url = info['info']['download_url']
    package.home_page = info['info']['home_page']
    package.description = info['info']['description']
    package.license = info['info']['license']
    package.summary = info['info']['summary']
    package.platform = info['info']['platform']
    package.downloads_month = info['info']['downloads']['last_month']
    package.downloads_week = info['info']['downloads']['last_week']
    package.downloads_day = info['info']['downloads']['last_day']

    author = s.query(Author).where(Package.id==package.id)
    author.name = info['info']['author']
    author.email=info['info']['author_email']
    author.package=package
    
    old_classifiers = s.query(Classifier).where(Package.id==package.id).all()
    for c in old_classifiers:
    	if not c.classifier in info['info']['classifiers']:
    		s.delete(c)
    	else:
    		info['info']['classifiers'].pop(info['info']['classifiers'].index(c.classifier))

    for c in info['info']['classifiers']:
        classifier = Classifier(classifier=c, package=package)
        s.add(classifier)

    # just nuke and re introduce releases and requirements since idk the best way to do it now
    for r in s.query(Release).where(Package.id==package.id).all():
    	s.delete(r) # *should* cascade to requirements? ._.

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

    print('[sql:update] updated records for '+package.name)

def remove_dead(pkg_name, s):
    """Remove records for a package that's disappeared."""
    package = s.query(Package).filter(Package.name==pkg_name).first()
    s.delete(package)
    print('[sql:drop] removed records for '+pkg_name)

def insert_build(resync_results, analysis_results, s):
    build = db.Build(rebuild_duration=resync_results['runtime'],
        analysis_duration=analysis_results['runtime'],
        index_count=resync_results['index_count'],
        real_count=resync_results['real_count'],
        phantom_count=resync_results['phantom_count'],
        packages_inserted=resync_results['packages_inserted'],
        packages_updated=resync_results['packages_updated'],
        packages_removed=resync_results['packages_removed'])
    s.add(build)
    print('[sql:insert] inserted new build #'+str(build.id))

    analaysis = db.Analysis(build=build,
        # General
        no_releases=analysis_results['no_releases'],
        no_url=analysis_results['no_url'],
        total_downloads=analysis_results['total_downloads'],
        total_current_downloads=analysis_results['total_current_downloads'],
        downloads_last_day=analysis_results['downloads_last_day'],
        downloads_last_week=analysis_results['downloads_last_week'],
        downloads_last_month=analysis_results['downloads_last_month'],
        top_required_packages=analysis_results['top_required_packages'],
        named_ecosystems=analysis_results['named_ecosystems'],
        home_page_domains=analysis_results['home_page_domains'],
        # Authors
        top_authors=analysis_results['top_authors'],
        unique_authors=analysis_results['unique_authors'],
        multiple_authors=analysis_results['multiple_authors'],
        author_email_domains=analysis_results['author_email_domains'],
        # Classifiers
        top_classifiers=analysis_results['top_classifiers'],
        framework_sizes_by_classifier=analysis_results['framework_sizes_by_classifier'],
        nonpython_pkgs=analysis_results['nonpython_pkgs'],
        natural_language_distribution=analysis_results['natural_language_distribution'],
        # Releases
        total_releases=analysis_results['total_releases'],
        current_releases=analysis_results['current_releases'],
        average_download_per_release=analysis_results['average_download_per_release'],
        major_version_distribution=analysis_results['major_version_distribution'],
        all_releases_size=analysis_results['all_releases_size'],
        current_releases_size=analysis_results['current_releases_size'],
        average_release_size=analysis_results['average_release_size'],
        average_release_interval=analysis_results['average_release_interval'],
        average_release_age=analysis_results['average_release_age'],
        # Requirements
        strong_weak_package_connections=analysis_results['strong_weak_package_connections'],
        packages_with_selfloops=analysis_results['packages_with_selfloops'],
        # Graphs
        package_requirement_graph=analysis_results['package_requirement_graph'],
        package_author_graph=analysis['package_author_graph'])
    s.add(analysis)
    print('[sql:insert] inserted analysis for build #'+str(build.id))
