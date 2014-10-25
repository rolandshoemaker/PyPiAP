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

def options_object(prefix, options):
	returner = {}
	for o in options:
		returner[o]['url'] = config.url+prefix+o
	return returner

def api_results_pager(thing, route, offset=0, limit=20):
	if not 'X-Total-Count' in request.headers:
		thing_length = len(thing)
		if thing_length >= limit:
			first_page = [config.url+route+'?offset=0&limit='+str(limit), 'first']
			last_page = [config.url+route+'?offset='+str(thing_length-(thing_length%limit))+'&limit='+str(thing_length%limit), 'last']
		else:
			first_page = [config.url+route+'?offset=0&limit='+str(thing_length), 'first']
			last_page = [config.url+route+'?offset=0&limit='+str(thing_length), 'last']
		next_page = ['', 'next']
		prev_page = ['', 'last']
		resp = Response(jsonify(things[offset:offset+limit]), status=200, mimetype='application/json')
		resp.headers['Link'] = ['<'+i[0]+'>; rel="'+i[1]+'",' for i in [first_page, last_page, next_page, prev_page]].join('\n')
		return 
	else:
		return thing

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
general_options = ['all',
	'no_releases',
	'no_url',
	'total_downloads',
	'total_current_downloads',
	'downloads_last_day',
	'downloads_last_week',
	'downloads_last_month',
	'top_required_packages',
	'named_ecosystems',
	'home_page_domains']
@app.route('/api/v1/general')
def api_general():
	resources = {'url': config.url+'/api/v1/general',
		'resources': options_object('/api/v1/general/', general_options)
	}
	return jsonify(resources)

@app.route('/api/v1/general/<option>')
def api_general_options(option):
	if option not in general_options: return not_found()

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

# Graphs
@app.route('/api/v1/graphs')
def api_graphs():
	pass

if __name__ == '__main__':
    app.debug = True
    app.run()
