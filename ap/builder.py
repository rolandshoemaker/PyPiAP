from sqlalchemy.orm import sessionmaker
from queue import Queue
from threading import Thread
from xml.etree import ElementTree
from urllib.request import urlopen
from urllib.error import HTTPError
from os.path import isfile, join
from os import listdir, remove
from sqlalchemy.orm import sessionmaker

from ap import db

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
                print('[new] '+dist) # it's a new entry
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
                    print('[update] '+dist) # it's an update to a already existing entry
                    # run update SQL stuff
                    # update_old(json.loads(b))
                    upd_queue.put(dist+'.json')
                    return True
    except HTTPError:
        print('[!] '+dist)
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
            print('[removed] '+f[:-5])
            # remove from sql
            del_queue.put(f[:-5])
            removed += 1
    return removed

def resync():
    """Update the package package index and incorporate those changes into pypi-json."""
    worker_num = 5
    pkg_queue = Queue()
    ins_queue = Queue()
    upd_queue = Queue()
    del_queue = Queue()

    # Get simple package index
    pkgs = get_distributions()
    index_len = len(pkgs)
    # Remove json files for packages that no longer exist
    pkgs_removed = clean_json_folder(pkgs)

    for p in pkgs:
       pkg_queue.put(p)

    # Start json_getters
    for i in range(worker_num):
       t = Thread(target=json_getter)
       t.daemon = True
       t.start()    

    pkg_queue.join()

    # Open db session
    session = sessionmaker()
    session.configure(autoflush=True, autocommit=False, bind=db.json_engine)
    s = session()

    # Get list of all json files.
    folder_list = [ f for f in listdir('/PyPiAP/json/') if isfile(join('/PyPiAP/json/',f)) ]
    real_len = len(folder_list)
    # Save number of 'phantom' packages (packages that are listed on the simple index but no /dist/json/ page exists.)
    phantom_len = index_len - real_len
    # Alphabetize so certain queries are optimized
    folder_list.sort()
    json_list = []
    old_json_list = []

    # Insert new records
    if ins_queue.qsize > 0:
        while True:
            f = ins_queue.get()
            o = open(join('/PyPiAP/json/',f), 'r')
            j = json.loads(o.read())
            json_list.append(j)
            o.close()
            db.insert_new(j, s)
            ins_queue.task_done()
            if ins_queue.qsize == 0:
                break

    # Update old records
    if upd_queue.qsize > 0:
        while True:
            f = upd_queue.get()
            o = open(join('/PyPiAP/json/',f), 'r')
            j = json.loads(o.read())
            old_json_list.append(j)
            o.close()
            db.update_old(j, s)
            upd_queue.task_done()
            if upd_queue.qsize == 0:
                break

    # Delete dead records
    if del_queue.qsize > 0:
        while True:
            f = del_queue.get()
            db.remove_dead(f, s)
            del_queue.task_done()
            if del_queue.qsize == 0:
                break

    # Add requirement records for new packages
    for j in json_list:
        db.new_requirements(j, s)

    # Update requirement records for old packages
    for j in old_json_list:
        db.update_requirements(j, s)