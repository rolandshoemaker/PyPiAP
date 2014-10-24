from ap import db

from flask import Flask, request, render_template, jsonify
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
		returner['o']['url'] = config.url+prefix+o
	return returner

# API routes
# return all the top level resources
@app.route('/api/v1/')
def api_index():
	resources = {'url': config.url+'api/v1/',
		'resources': {}
	}
	endpoints = [url_for(i) for i in app.url_map.iter_rules() if urllib.parse.urlparse(url_for(i)).path.startswith('/api/v1/') and len(urllib.parse.urlparse(url_for(i)).path.split('/')) == 4]
	for e in endpoints:
		if not e.split('/')[-1] == '':
			resources['resources'][e.split('/')[-1]]['url'] = e
	return jsonify(resources)

# General
general_options = ['all']
@app.route('/api/v1/general')
def api_general():
	resources = {'url': config.url+'api/v1/general',
		'resources': {}
	}
	resources['resources'] = options_object('api/v1/general/', general_options)
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

# Tarballs
@app.route('/api/v1/tarballs')
def api_tarballs():
	pass

if __name__ == '__main__':
    app.run()
