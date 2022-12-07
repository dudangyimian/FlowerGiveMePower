import os


bind = ":4096"

workers = os.cpu_count() * 2 -1

cur_dir = os.path.dirname(__file__)

loglevel = 'warning'

errorlog = os.path.join(cur_dir,"error.log")


accesslog = os.path.join(cur_dir,"access.log")