Python Package index Analysis Project
=====================================

collection of various tools written to help analyze the Python Package index ([PyPi](https://pypi.python.org/pypi)). at some point i'll add a link here to the project page on my website that will show all the pretty graphics and stuff yay ^_^

Module structure
-----------------

    -- ap
      -- db.py # database related stuff
      -- buidler.py # tools to build/resync the pypi-json database with PyPi
      -- config.py # config variables
      --> utils # utility functions that may be reused
        -- peeper.py # tool to extract requirements from tarballs/zips
      --> analysis # various collections of tests to run against data in pypi-json
        -- authors.py
        -- releases.py
        -- classifiers.py

Analysis
--------

stuff that we should look at to do things

* **staleness**
 * how stale are packages? (is most recent release old) [&#10004;]
 * are there stale packages with high recent downloads?  
* **authors**
 * number of authors contributing to more than 1 package etc [&#10004;]
 * how many packages attribute multiple authors [&#10004;]
 * how many packages attribute orginization
 * what are author email tld's? (.gov, .edu, etc...) [&#10004;]
* **requirements**
 * link network between all current releases of packages! (using the requirement extractor on tarballs)
 * what are the most used requirements? (seriously what is actually the most used package)
* **packages**
 * naming schemes
  * sub-ecosystems (e.g. how many packages use the django-/flask- or django./flask. prefix)
 * what licenses do people use? (connected to classifiers as well?)
* **classifiers**
 * what are the most popular classifiers [&#10004;]
 * does more classifiers == more downloads?
 * how do people use the version classifiers
 * what license do people use?
* **releases**
 * average time between releases [&#10004;]
 * average size of releases (sdist vs. bdist)
 * major version distribution [&#10004;]
* **URLS** 
 * where do people point their download url to?
 * where do people point their homepage url to?
* **overall health**
 * how many packages listed have no info at all (i.e. dead json link) [&#10004;]
 * how many packages have no releases/urls [releases &#10004;]
 * how many packages have no description/bad(?) classifiers/no homepage/no author info/etc
 * makeup of index by version
 * total sdist size of index/total bdist size of index [sdist &#10004;]
 * total size of JSON index (more for us but w/e)
 * total downloads this week/month across all packages [&#10004;]
 * total downloads ever across all releases/most recent releases [&#10004;]
