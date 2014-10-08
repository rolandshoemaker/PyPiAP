#!/usr/bin/python3
from xml.etree import ElementTree
from urllib.request import urlopen
from urllib.error import HTTPError
import json, os.remove
from os.path import isfile, join
from os import listdir
from queue import Queue
from threading import Thread

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
            if not isfile('/PyPiAP/json/'+dist):
                o = open('/PyPiAP/json/'+dist+'.json', 'w')
                o.write(f.readall().decode('utf-8'))
                o.close()
                print('[new] '+dist) # it's a new entry
                # run insert SQL stuff
                return True
            else:
                a = open('/PyPiAP/json/'+dist, 'r').readall().decode('utf-8')
                b = f.readall().decode('utf-8')
                if not a == b:
                    o = open('/PyPiAP/json/'+dist+'.json', 'w')
                    o.write(b)
                    o.close()
                    print('[update] '+dist) # it's an update to a already existing entry
                    # run update SQL stuff
                    return True
    except HTTPError:
        print('[!] '+dist)
        return False

def json_getter():
    while True:
        item = pkg_queue.get()
        get_pkg_json(item)
        pkg_queue.task_done()

def clean_json_folder(pkg_list):
    """Remove any package.json file that no longer exists and return the number removed."""
    folder_list = [ f for f in listdir('/PyPiAP/json/') if isfile(join('/PyPiAP/json/',f)) ]
    removed = 0
    for f in folder_list:
        if not f in pkg_list:
            os.remove(join('/PyPiAP/json/',f))
            removed += 1
    return removed

worker_num = 3
pkg_queue = Queue()

for i in range(worker_num):
    t = Thread(target=json_getter)
    t.daemon = True
    t.start()    

pkgs = get_distributions()
clean_json_folder(pkgs)

for p in pkgs:
    pkg_queue.put(p)

pkg_queue.join()
