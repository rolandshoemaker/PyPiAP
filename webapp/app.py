from ap import db, config

from flask import Flask, request, render_template, jsonify, url_for, Response
import urllib.parse
# Maybe split front-end and api routes into different files? (not really sure how to do this)
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

def api_results_pager(thing, route, offset=0, limit=20):
	if not 'X-Total-Count' in request.headers:
		thing_length = len(thing) # does this need to be -1?
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
		resp = Response(jsonify(things[offset:offset+limit]), status=200, mimetype='application/json')
		resp.headers['Link'] = ['<'+i[0]+'>; rel="'+i[1]+'"' for i in [first_page, last_page, next_page, prev_page]].join(',\n')
		return 
	else:
		return jsonify(thing)

def build_analysis_to_json(build, prefix, normal_columns, big_columns):
	returner = {'build_id': build.build_id,
		'build_timestamp': build.build.build_timestamp,
		'analysis': {}}
	filter = request.args.get('fields', None)

	if filter:
		filters = filter.split(',')
		normal_columns, big_columns = [c for c in normal_columns if c in filters], [c for c in big_columns if c in filters]

	for c in normal_columns:
		returner['analysis'][c] = build.__dict__[c]

	for c in big_columns:
		returner['analysis'][c] = {'url': config.url+prefix+'/'+c+'/'+build.build_id}

	return returner

# API routes
# return all the top level resources
@app.route('/api/v1/')
def api_index():
	resources = {'url': config.url+'/api/v1',
		'resources': {}
	}
	endpoints = [config.url+str(i) for i in app.url_map.iter_rules() if str(i).startswith('/api/v1/') and len(str(i).split('/')) == 4]
	for e in endpoints:
		if not e.split('/')[-1] == '':
			resources['resources'][e.split('/')[-1]] = {'url': e}
	return jsonify(resources)

# General
@app.route('/api/v1/general', defaults={'build_id': None})
@app.route('/api/v1/general/<int:build_id>')
def api_general(build_id):
	# allow time series query here (mb decorator), if no query return most recent build
	normal = ['no_releases', 'no_url', 'total_downloads', 'total_current_downloads', 'downloads_last_day', 'downloads_last_week', 'downloads_last_month']
	objects = ['top_required_packages', 'named_ecosystems', 'home_page_domains']

	if not build_id:
		general_analysis = [s.query(db.General_analysis).order_by('-id').first()]
	elif request.args.get('timeseries', None):
		# pagination here?
		timeseries_ids = []
		general_analysis = [s.query(db.General_analysis).filter(db.Build.id==tid).first() for tid in timeseries_ids]
	else:
		general_analysis = [s.query(db.General_analysis).filter(db.Build.id==build_id).first()]

	if len(general_analysis) < 1:
		# bad build_id, probably better error code?
		return not_found()
	else:
		# impl sort here?
		return jsonify([build_analysis_to_json(i, '/api/v1/general', normal, objects) for i in general_analysis])

@app.route('/api/v1/general/top_required_packages', defaults={'build_id': None})
@app.route('/api/v1/general/top_required_packages/<int:build_id>')
def api_general_top_required_packages(build_id):
	pass

@app.route('/api/v1/general/named_ecosystems', defaults={'build_id': None})
@app.route('/api/v1/general/named_ecosystems/<int:build_id>')
def api_general_top_required_packages(build_id):
	pass

@app.route('/api/v1/general/home_page_domains', defaults={'build_id': None})
@app.route('/api/v1/general/home_page_domains/<int:build_id>')
def api_general_top_required_packages(build_id):
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
