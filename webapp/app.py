from ap import db

from flask import Flask, request, render_template, jsonify
# Maybe split front-end and api routes into different files? (not really sure how to do this)
app = Flask(__name__)
s = db.make_session(db.stats_engine, scoped=True)

# Front-end routes
@app.route('/')
def hello():
    return render_template('index.html')

# API routes
@app.route('/api/v1/')
def api_index():
	resources = {'url': config.url+'api/v1/',
		'resources': {
			'general': {
				'url': config.url+'api/v1/general'
			},
			'authors': {
				'url': config.url+'api/v1/authors'
			},
			'classifiers': {
				'url': config.url+'api/v1/classifiers'
			},
			'releases': {
				'url': config.url+'api/v1/releases'
			},
			'requirements': {
				'url': config.url+'api/v1/requirements'
			},
			'graphs': {
				'url': config.url+'api/v1/graphs'
			},
			'tarballs': {
				'url': config.url+'api/v1/tarballs'
			}
		}
	}
	return jsonify(resources)

if __name__ == '__main__':
    app.run()
