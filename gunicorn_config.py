import gevent.monkey
import multiprocessing

"""
gunicorn的配置文件
"""
# gevent的猴子魔法 变成非阻塞
gevent.monkey.patch_all()

bind = '192.168.15.10:9000'

# 启动的进程数
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gunicorn.workers.ggevent.GeventWorker'