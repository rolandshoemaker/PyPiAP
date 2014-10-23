from flask import Flask, request, render_template
import json
# Maybe split front-end and api routes into different files? (not really sure how to do this)
app = Flask(__name__)

# Front-end routes
@app.route('/')
def hello():
    return render_template('index.html')

# API routes

if __name__ == '__main__':
    app.run()