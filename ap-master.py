from webapp.app import app
from ap import builder, db

import multiprocessing
import schedule
from redis import Redis
redis = Redis()

def web_server():
	app.run()

def rebuild():
	builder.rebuild()

d = multiprocessing.Process(name='ap-web_server', target=web_server)
d.daemon = True
d.start()

schedule.every().monday().do(rebuild)

while True:
	# add some way to force a rebuild via a command line tool also (mb some queue, redis/rabbitmq/celery/etc?)
    schedule.run_pending()
    time.sleep(1)
