import multiprocessing

bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1

chddir = 'app/'

# Require setproctitle module
#proc_name = 'lexpage'

max_request = 200
max_requests_jitter = 20

# We need this for markup preview
limit_request_line = 8190

pidfile = 'gunicorn.pid'
errorlog = 'gunicorn.log'
loglevel = 'error'
