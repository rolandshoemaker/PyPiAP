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

def analysis_to_json(build, prefix, normal_columns, big_columns):
	# add filtering+sorting+field select here?
	returner = {'build_id': build.build_id,
		'build_timestamp': build.build.build_timestamp,
		'analysis': {}}
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
@app.route('/api/v1/general')
def api_general():
	current_analysis = s.query(db.General_analysis).order_by('-id').first()
	normal = ['no_url', 'total_downloads', 'total_current_downloads', 'downloads_last_day', 'downloads_last_week', 'downloads_last_month']
	objects = ['top_required_packages', 'named_ecosystems', 'home_page_domains']
	return jsonify(analysis_to_json(current_analysis, '/api/v1/general', normal, objects))
	# return jsonify({'build_id': current_analysis.build_id,
	# 	'build_timestamp': s.query(db.Build.build_timestamp).filter(db.Build.id==current_analysis.build_id).first()[0],
	# 	'analysis': {'no_releases': current_analysis.no_releases,
	# 		'no_url': current_analysis.no_url,
	# 		'total_downloads': current_analysis.total_downloads,
	# 		'total_current_downloads': current_analysis.total_current_downloads,
	# 		'downloads_last_day': current_analysis.downloads_last_day,
	# 		'downloads_last_week': current_analysis.downloads_last_week,
	# 		'downloads_last_month': current_analysis.downloads_last_month,
	# 		'top_required_packages': {'url': config.url+'/api/v1/general/top_required_packages/'+current_analysis.build_id},
	# 		'named_ecosystems': {'url': config.url+'/api/v1/general/named_ecosystems/'+current_analysis.build_id},
	# 		'home_page_domains': {'url': config.url+'/api/v1/general/home_page_domains/'+current_analysis.build_id}
	# })

@app.route('/api/v1/general/top_required_packages/<int:build_id>')
def api_general_top_required_packages(build_id=None):
	pass

@app.route('/api/v1/general/named_ecosystems/<int:build_id>')
def api_general_top_required_packages(build_id=None):
	pass

@app.route('/api/v1/general/home_page_domains/<int:build_id>')
def api_general_top_required_packages(build_id=None):
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
