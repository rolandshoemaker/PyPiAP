from ap import db, config

from flask import Flask, request, render_template, jsonify, url_for, Response
import urllib.parse
# Maybe split front-end and api routes+stuff into different files? (not really sure how to do this)
app = Flask(__name__)
s = db.make_session(db.stats_engine, scoped=True)

# Front-end routes
@app.route('/')
def hello():
    return render_template('index.html')

# API utilities
@app.errorhandler(404)
def not_found(error=None):
	message = {
		'status': 404,
		'message': 'Not Found: '+request.url
	}
	resp = jsonify(message)
	resp.status_code = 404
	return resp

def api_pager(ids, route, offset=0, limit=20):
	if not 'X-Total-Count' in request.headers:
		thing_length = len(ids)-1 # does this need to be -1?
		if thing_length >= limit:
			first_page = [config.url+route+'?offset=0&limit='+str(limit), 'first']
			last_page = [config.url+route+'?offset='+str(thing_length-(thing_length%limit))+'&limit='+str(thing_length%limit), 'last']
		else:
			first_page = [config.url+route+'?offset=0&limit='+str(thing_length), 'first']
			last_page = [config.url+route+'?offset=0&limit='+str(thing_length), 'last']
			limit = thing_length

		if offset+limit > thing_length:
			return not_found() # bail since asking for range thats not existy, better error code..?

		next_page = ['', 'next']
		prev_page = ['', 'last']

		paged_links = ['<'+i[0]+'>; rel="'+i[1]+'"' for i in [first_page, last_page, next_page, prev_page]].join(',\n')
		return ids[offset:offset+limit], paged_links
	else:
		return ids, None

def api_object_pager(object, offset=0, limit=20, links=False):
	pass

def api_build_analysis_to_json(build, prefix, normal_columns, big_columns):
	returner = {'build_id': build.build_id,
		'build_timestamp': build.build.build_timestamp,
		'analysis': {}}
	filters = request.args.get('fields', None)

	if filters:
		filters = filters.split(',')
		normal_columns, big_columns = [c for c in normal_columns if c in filters], [c for c in big_columns if c in filters]

	for c in normal_columns:
		returner['analysis'][c] = build.__dict__[c]

	for c in big_columns:
		# check if expanded=true, if so show partially expanded big columns (still not full, useobject_pager defaults?!)
		if request.args.get('expanded', None):
			returner['analysis'][c] = {'url': config.url+prefix+'/'+c+'/'+build.build_id, 'object': api_object_pager(build.__dict__[c])}
		else:
			returner['analysis'][c] = {'url': config.url+prefix+'/'+c+'/'+build.build_id}

	return returner

def api_analysis_table():
	pass

# API routes
# return all the top level resources
@app.route('/api/v1/')
def api_index():
	resources = {'url': config.url+'/api/v1', 'resources': {}}
	endpoints = [config.url+str(i) for i in app.url_map.iter_rules() if str(i).startswith('/api/v1/') and len(str(i).split('/')) == 4]
	for e in endpoints:
		if not e.split('/')[-1] == '':
			resources['resources'][e.split('/')[-1]] = {'url': e}
	return jsonify(resources)

# General
@app.route('/api/v1/general', defaults={'build_id': None})
@app.route('/api/v1/general/<int:build_id>')
def api_general(build_id):
	normal = ['no_releases', 'no_url', 'total_downloads', 'total_current_downloads', 'downloads_last_day', 'downloads_last_week', 'downloads_last_month']
	objects = ['top_required_packages', 'named_ecosystems', 'home_page_domains']

	# allow time series query here (mb decorator), if no query return most recent build
	# two args, timeseries for build_id to build_id, and lazy_timeseries from generating build_ids from timestamp to timestamp
	if request.args.get('timeseries', None) and not build_id:
		# pagination here?
		offset = request.args.get('offset', 0)
		limit = request.args.get('limit', 20)
		# something here to generate list of ids from two dates... (also a way to handle how i have it now, comma-list of ids)
		timeseries_ids = request.args.get('timeseries').split(',')
		paged_ids, paged_links = api_pager(timeseries_ids, '/api/v1/general', offset, limit)
		general_analysis = [s.query(db.General_analysis).filter(db.Build.id==tid).first() for tid in paged_ids]
	elif not build_id:
		general_analysis = [s.query(db.General_analysis).order_by('-id').first()]
	elif build_id:
		general_analysis = [s.query(db.General_analysis).filter(db.Build.id==build_id).first()]
	else:
		return not_found()

	if len(general_analysis) < 1:
		# bad build_id, probably better error code?
		return not_found()
	else:
		# impl sort here?
		columns = [api_build_analysis_to_json(i, '/api/v1/general', normal, objects) for i in general_analysis]
		resp = jsonify(columns)
		resp.status_code = 200
		if paged_links: resp.headers['Link'] = paged_links
		return resp

@app.route('/api/v1/general/top_required_packages', defaults={'build_id': None})
@app.route('/api/v1/general/top_required_packages/<int:build_id>')
def api_general_top_required_packages(build_id):
	pass

@app.route('/api/v1/general/named_ecosystems', defaults={'build_id': None})
@app.route('/api/v1/general/named_ecosystems/<int:build_id>')
def api_general_named_ecosystems(build_id):
	pass

@app.route('/api/v1/general/home_page_domains', defaults={'build_id': None})
@app.route('/api/v1/general/home_page_domains/<int:build_id>')
def api_general_home_page_domains(build_id):
	pass

# Authors
@app.route('/api/v1/authors')
def api_authors():
	pass

# Classifiers
@app.route('/api/v1/classifiers')
def api_classifiers():
	pass

# Releases
@app.route('/api/v1/releases')
def api_releases():
	pass

# Requirements
@app.route('/api/v1/requirements')
def api_requirements():
	pass

# Tarballs
@app.route('/api/v1/tarballs')
def api_tarballs():
	pass

if __name__ == '__main__':
    app.debug = True
    app.run()
