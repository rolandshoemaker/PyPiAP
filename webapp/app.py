from ap import db, config

from flask import Flask, request, render_template, jsonify, url_for, Response
#import urlparse
import dateutil.parser
import logging

# Maybe split front-end and api routes+stuff into different files? (not really sure how to do this)
app = Flask(__name__)
file_handler = logging.FileHandler(config.root_dir+'logs/flask.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
s = db.make_session(db.stats_engine, scoped=True)

# Front-end routes
@app.route('/')
def hello():
    return render_template('index.html')

# API utility functions
@app.errorhandler(404)
def not_found(error=None):
	message = {
		'status': 404,
		'message': 'Not Found: '+request.url
	}
	resp = jsonify(message)
	resp.status_code = 404
	return resp

@app.errorhandler(400)
def bad_request(error=None):
	message = {
		'status': 400,
		'message': 'Bad Request'
	}
	if error:
		message['message'] += ': '+error
	resp = jsonify(message)
	resp.status_code = 400
	return resp

def api_pager(ids, route=None, offset=0, limit=20, links=True):
	if not 'X-Total-Count' in request.headers:
		thing_length = len(ids)-1 # does this need to be -1?
		if links and route:
			if thing_length >= limit:
				first_page = [config.url+route+'?offset=0&limit='+str(limit), 'first']
				last_page = [config.url+route+'?offset='+str(thing_length-(thing_length%limit))+'&limit='+str(thing_length%limit), 'last']
			else:
				first_page = [config.url+route+'?offset=0&limit='+str(thing_length), 'first']
				last_page = [config.url+route+'?offset=0&limit='+str(thing_length), 'last']
				limit = thing_length

			if offset+limit > thing_length:
				return bad_request('offset + limit is more than the resource length') # bail since asking for range thats not existy, better error code..?

			next_page = ['', 'next']
			prev_page = ['', 'last']

			paged_links = ['<'+i[0]+'>; rel="'+i[1]+'"' for i in [first_page, last_page, next_page, prev_page]].join(',\n')
			return ids[offset:offset+limit], paged_links
		else:
			return ids[offset:offset+limit]
	else:
		return ids, None

def api_object_pager(thing, route=None, offset=0, limit=20, links=False):
	# monkey-patch, this is not what this is meant for whoopsy lol
	if links and route:
		return api_pager(thing, route=route, offset=offset, limit=limit)
	else:
		return api_pager(thing, offset=offset, limit=limit, links=links)

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
			returner['analysis'][c] = {'url': config.url+prefix+'/'+c+'/'+build.build_id, 'partial_object': api_object_pager(build.__dict__[c])}
		else:
			returner['analysis'][c] = {'url': config.url+prefix+'/'+c+'/'+build.build_id}

	return returner

def api_analysis_table():
	# populate from api_general prototype
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
		# time series!
		offset = request.args.get('offset', 0)
		limit = request.args.get('limit', 20)
		timeseries_ids = request.args.get('timeseries').split('-')
		if not len(timeseries_ids) == 2 and (timeseries_ids[0] < 0 or timeseries_ids[0] >= timeseries_ids[1]):
			# bad timeseries!
			return bad_request('Invalid timeseries')
		paged_ids, paged_links = api_pager(range(timeseries_ids[0], timeseries_ids[1]+1), '/api/v1/general', offset, limit)
		general_analysis = [s.query(db.General_analysis).filter(db.Build.id==tid).first() for tid in paged_ids]
	elif request.args.get('lazy_timeseries', None):
		# lazy timeseries!
		lazy_series = request.args.get('lazy_timeseries').split('-')
		# prob wanna try/catch this for parsing errors
		if not len(lazy_series) == 2 and (dateutil.parser.parse(lazy_series[0]) < 0 or dateutil.parser.parse(lazy_series[0]) >= lazdateutil.parser.parse(lazy_series[1])):
			# bad lazy series!
			return bad_request('Invalid lazy_timeseries') # definitely not right error code!
		# timestamp format ISO 8601: 20130903T13:17:45Z
		lazy_series = [dateutil.parser.parse(lazy_series[0]), dateutil.parser.parse(lazy_series[1])]
		build_timestamps = s.query(db.Build.id, db.Build.build_timestamp).all()
		low_time = min([b[1] for b in build_timestamps], key=lambda x:abs(x-lazy_series[0]))
		low_id = [b[0] for b in build_timestamps if b[1] == low_time][0]
		high_time = min([b[1] for b in build_timestamps], key=lambda x:abs(x-lazy_series[1]))
		high_id = [b[0] for b in build_timestamps if b[1] == high_time][0]
		paged_ids, paged_links = api_pager(range(low_id, high_id+1), '/api/v1/general', offset, limit)
		general_analysis = [s.query(db.General_analysis).filter(db.Build.id==tid).first() for tid in paged_ids]
	elif not build_id:
		# no args at all! return most recent build
		general_analysis = [s.query(db.General_analysis).order_by('-id').first()]
	elif build_id:
		# build id specified, return it
		general_analysis = [s.query(db.General_analysis).filter(db.Build.id==build_id).first()]
		if len(general_analysis) == 0:
			return bad_request('Invalid build_id')
	else:
		# idk what happened...
		return not_found()

	if len(general_analysis) < 1:
		# bad build_id or something, probably better error code?
		return not_found()
	else:
		stuff = [api_build_analysis_to_json(i, '/api/v1/general', normal, objects) for i in general_analysis]
		if request.args.get('sort', None):
			sorters = request.args.get('sort')
			for sorter in reversed(sorters):
				reverse = True # default to descending list
				if sorter.startswith('+'):
					# oh you want aescending... fine
					reverse = False
				try:
					stuff.sort(key=lambda x:x.analysis.__dict__[sorter], reverse=reverse)
				except KeyError:
					# bad query!
					return bad_request(sorter+' is a invalid sort key')
		resp = jsonify(stuff)
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
