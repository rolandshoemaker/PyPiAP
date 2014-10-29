from sqlalchemy.orm import sessionmaker
from queue import Queue
from threading import Thread
from xml.etree import ElementTree
from urllib.request import urlopen
from urllib.error import HTTPError
from os.path import isfile, join
from os import listdir, remove
from sqlalchemy.orm import sessionmaker
import datetime, logging

from ap import db, config

logging.config.fileConfig(config.root_dir+'logging.conf')
logger = logging.getLogger('Builder')

def get_distributions(simple_index='https://pypi.python.org/simple/'):
    """Gets a simple list of packages PyPi tracks."""
    with urlopen(simple_index) as f:
        tree = ElementTree.parse(f)
    return [a.text for a in tree.iter('a')]

def get_pkg_json(dist):
    """Retrieves the JSON file for package name dist and writes it to file, it returns true if the 
    file is created or false if the json file couldn't be found on PyPi."""
    # should implement some check to only write if it has changed... or just return
    # the json, and let SQLalchemy check if the record exists/has changed?
    try:
        with urlopen('https://pypi.python.org/pypi/' + dist + '/json/') as f:
            if not isfile('/PyPiAP/json/'+dist+'.json'):
                o = open('/PyPiAP/json/'+dist+'.json', 'w')
                contents = f.readall().decode('utf-8')
                o.write(contents)
                o.close()
                logger.info('[new] '+dist) # it's a new entry
                # run insert SQL stuff
                # insert_new(json.loads(contents))
                ins_queue.put(dist+'.json')
                return True
            else:
                a = open('/PyPiAP/json/'+dist+'.json', 'r').read() #.decode('utf-8')
                b = f.readall().decode('utf-8')
                if not a == b:
                    o = open('/PyPiAP/json/'+dist+'.json', 'w')
                    o.write(b)
                    o.close()
                    logger.info('[update] '+dist) # it's an update to a already existing entry
                    # run update SQL stuff
                    # update_old(json.loads(b))
                    upd_queue.put(dist+'.json')
                    return True
    except HTTPError:
        logger.error('[!] '+dist)
        return False

def json_getter():
    """Wrapper for threaded JSON getting."""
    while True:
        item = pkg_queue.get()
        get_pkg_json(item)
        pkg_queue.task_done()
        if pkg_queue.qsize == 0:
            break

def clean_json_folder(pkg_list):
    """Remove any package.json file that no longer exists and return the number removed."""
    folder_list = [ f for f in listdir('/PyPiAP/json/') if isfile(join('/PyPiAP/json/',f)) ]
    removed = 0
    for f in folder_list:
        if not f[:-5] in pkg_list:
            remove(join('/PyPiAP/json/',f))
            logger.info('[removed] '+f[:-5])
            # remove from sql
            del_queue.put(f[:-5])
            removed += 1
    return removed

def resync(s):
    """Update the package package index and incorporate those changes into pypi-json."""
    worker_num = 5
    pkg_queue = Queue()
    ins_queue = Queue()
    upd_queue = Queue()
    del_queue = Queue()
    start_time = datetime.datetime.now()

    # Get simple package index
    logger.info("# Fetching Simple index.")
    pkgs = get_distributions()
    index_len = len(pkgs)
    # Remove json files for packages that no longer exist
    logger.info("# Removing JSON files for dead packages.")
    pkgs_removed = clean_json_folder(pkgs)

    for p in pkgs:
       pkg_queue.put(p)

    # Start json_getters
    logger.info("# Retreiving JSON files.")
    for i in range(worker_num):
       t = Thread(target=json_getter)
       t.daemon = True
       t.start()    

    pkg_queue.join()

    # Get list of all json files.
    folder_list = [ f for f in listdir('/PyPiAP/json/') if isfile(join('/PyPiAP/json/',f)) ]
    real_len = len(folder_list)
    # Save number of 'phantom' packages (packages that are listed on the simple index but no /dist/json/ page exists.)
    phantom_len = index_len - real_len
    # Alphabetize so certain queries are optimized
    folder_list.sort()
    json_list = []
    old_json_list = []

    # This whole section could probably be multi-threaded
    # Insert new records
    ins_num = ins_queue.qsize
    if ins_queue.qsize > 0:
        logger.info("# Inserting records for new packages.")
        while True:
            f = ins_queue.get()
            o = open(join('/PyPiAP/json/',f), 'r')
            j = json.loads(o.read())
            json_list.append(j)
            o.close()
            db.insert_new(j, s)
            s.commit()
            ins_queue.task_done()
            if ins_queue.qsize == 0:
                break

    # Update old records
    upd_num = upd_queue.qsize
    if upd_queue.qsize > 0:
        logger.info("# Updating records for old packages.")
        while True:
            f = upd_queue.get()
            o = open(join('/PyPiAP/json/',f), 'r')
            j = json.loads(o.read())
            old_json_list.append(j)
            o.close()
            db.update_old(j, s)
            s.commit()
            upd_queue.task_done()
            if upd_queue.qsize == 0:
                break

    # Delete dead records
    if del_queue.qsize > 0:
        logger.info("# Deleting records for dead packages.")
        while True:
            f = del_queue.get()
            db.remove_dead(f, s)
            s.commit()
            del_queue.task_done()
            if del_queue.qsize == 0:
                break

    # This part should prob be multi-thread too... (but after the first one?)
    # Add requirement records for new packages
    logger.info("# Building requirement network.")
    for j in json_list:
        db.new_requirements(j, s)
        s.commit()

    # Update requirement records for old packages
    for j in old_json_list:
        db.update_requirements(j, s)
        s.commit()

    s.close()
    end_time = datetime.datetime.now()
    logger.info("# Finished, runtime: "+str(end_time - start_time)+".")

    # Return stats about what we did done
    return {'index_count': index_len,
        'real_count': real_len,
        'phantom_count': phantom_size,
        'packages_inserted': ins_num,
        'packages_updated': upd_num,
        'packages_removed': pkgs_removed,
        'runtime': end_time - start_time}

def analyze(s):
    start_time = datetime.datetime.now()

    # Graphs
    graphs = {}
    graphs['package_requirement_graph'] = create_graph(get_pkg_nodelist(s), get_pkg_edgelist(s))
    graphs['package_author_graph'] = create_graph(get_author_nodelist(s), get_author_edgelist(s))
    # General
    general = {}
    general['no_releases'] = ap.analysis.general.no_releases(s)
    general['no_urls'] = ap.analysis.general.no_urls(s)
    download_dict = ap.analysis.general.downloads(s)
    general['total_downloads'] = download_dict['all_time_total']
    general['total_current_downloads'] = download_dict['current_total']
    general['downloads_last_day'] = download_dict['last_day']
    general['downloads_last_week'] = download_dict['last_week']
    general['downloads_last_month'] = download_dict['last_month']
    general['top_required_packages'] = ap.analysis.general.top_required_packages(s, g=graphs['package_requirement_graph'])
    general['named_ecosystems'] = ap.analysis.general.find_named_ecosystems(s, cutoff=0, g=graphs['package_requirement_graph'])
    general['home_page_domains'] = ap.analysis.general.home_page_domains(s, cutoff=0)
    # Authors
    author = {}
    author['top_authors'] = ap.analysis.authors.top_authors(s)
    author['unique_authors'] = ap.analysis.authors.unique_authors(s)
    author['multiple_authors'] = ap.analysis.authors.multiple_authors(s)
    author['author_email_domains'] = ap.analysis.authors.author_email_domains(s, cutoff=0)
    # Classifiers
    classifier = {}
    classifier['top_classifiers'] = ap.analysis.classifiers.top_classifiers(s, cutoff=0)
    classifier['framework_sizes_by_classifier'] = ap.analysis.classifiers.framework_sizes_by_classifier(s)
    classifier['nonpython_pkgs'] = ap.analysis.classifiers.nonpython_pkgs(s)
    classifier['natural_language_distribution'] = ap.analysis.classifiers.natural_language_distribution(s)
    # Releases
    release = {}
    release['total_releases'] = ap.analysis.releases.num(s)
    release['current_releases'] = ap.analysis.releases.current_num(s)
    release['average_download_per_release'] = ap.analysis.releases.avg_downloads(s)
    release['major_version_distribution'] = ap.analysis.releases.major_version_distribution(s)
    release['all_releases_size'] = ap.analysis.releases.total_size(s)
    release['current_releases_size'] = ap.analysis.releases.current_size(s)
    release['average_release_size'] = ap.analysis.releases.avg_size(s)
    release['average_release_interval'] = ap.analysis.releases.avg_release_interval(s)
    release['average_release_age'] = ap.analysis.releases.avg_release_age(s)
    # Requirements
    requirement = {}
    requirement['strong_weak_package_connections'] = ap.analysis.requirements.strong_weak_package_connections(s, g=graphs['package_requirement_graph'])
    requirement['packages_with_selfloops'] = ap.analysis.requirements.packages_with_selfloops(s, g=graphs['package_requirement_graph'])

    end_time = datetime.datetime.now()

    return {'runtime': end_time - start_time,
        'General': general,
        'Authors': author,
        'Classifiers': classifier,
        'Releases': release,
        'Requirements': requirement,
        'Graphs:': graphs}

def rebuild():
    s = db.make_session(db.json_engine)

    # resync the JSON db (pypi-json)
    resync_results = resync(s)

    # run analysis methods
    analysis_results = analyze(s)

    # add resync results + analysis results to stats db (pypi-stats)
    db.insert_build(resync_results, analysis_results, s)
    s.commit()
    s.close()
    