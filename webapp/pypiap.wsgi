import sys
from ap import config
sys.path.insert(0, config.root_dir)
from webapp.app import app as application
