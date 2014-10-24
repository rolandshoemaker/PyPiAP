from webapp.app import app
from ap import builder, db, config

import multiprocessing
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BlockingScheduler(jobstores={'apscheduler.jobstores.default': 
	{'type': 'sqlalchemy',
	'url': config.db+'builder-jobs'}},
	job_defaults={'max_instances': 1})

def rebuild():
	builder.rebuild()

def web_server():
	app.run()

d = multiprocessing.Process(name='ap-web_server', target=web_server)
d.daemon = True
d.start()

scheduler.add_cron_job(rebuild,
	jobstore="apschedulerJobs",
	id=0,
	replace_existing=True,
	'interval',
	weeks=1)
scheduler.start()