#!/usr/bin/python3
from xml.etree import ElementTree
from urllib.request import urlopen
from urllib.error import HTTPError
import json
from os.path import isfile, join
from os import listdir, remove
from queue import Queue
from threading import Thread

import JSONmodels

def insert_new(info):
    package = JSONmodels.Package(name=info['info']['name'],
        download_url=info['info']['download_url'],
        home_page=info['info']['home_page'],
        description=info['info']['description'],
        license=info['info']['license'],
        summary=info['info']['summary'],
        platform=info['info']['platform'])
    s.add(package)
    author = JSONmodels.Author(name=info['info']['author'],
        email=info['info']['author_email'],
        package=package)
    a.add(author)
    for c in info['info']['classifiers']:
        classifier = JSONmodels.Classifier(classifier=c, package=package)
        s.add(classifier)
    for version, pkgs in info['releases'].iteritems():
	for i, p in enumerate(pkgs):
            is_url = p in info['urls']
            current = version == info['info']['version']
            release = JSONmodels.Release(version=version,
                current=current,
                is_url=is_url,
                upload_time=strptime(info['release'][i]['upload_time'], '%Y-%m-%dT%H:%M:%S'),
                python_version=info['release'][i]['python_version'],
                comment_text=info['release'][i]['comment_text'],
                has_sig=info['release'][i]['has_sig'],
                filename=info['release'][i]['filename'],
                packagetype=info['release'][i]['packagetype'],
                size=info['release'][i]['size'],
                downloads=info['release'][i]['downloads'],
                package=package)
            s.add(release)
            # do requirement extracting here or elsewhere?

def update_old(info):
    pass

def remove_dead(pkg_name):
    s.query(Package).filder(Package.name==pkg_name).delete()
    s.commit()

def get_distributions(simple_index='https://pypi.python.org/simple/'):
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
                    return True
    except HTTPError:
        print('[!] '+dist)
        return False

def json_getter():
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
            # remove_dead(f[:-5])
            removed += 1
    return removed



#worker_num = 5
#pkg_queue = Queue()

#pkgs = get_distributions()
#clean_json_folder(pkgs)

#for p in pkgs:
#    pkg_queue.put(p)

#for i in range(worker_num):
#    t = Thread(target=json_getter)
#    t.daemon = True
#    t.start()    

#pkg_queue.join()
