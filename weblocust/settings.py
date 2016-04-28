#coding:utf-8

##
#  system options(infomations that both master and slave needs)
##

REDIS_SERVER = "localhost"
NODE_ROLE = "master" # master or slave
MASTER_ADDRESS = "10.0.0.100"
MASTER_PORT = 9999

##
#  master options
##

DETECT_ZOMBIE_FRENQUENCY = 10  # seconds
REQUEST_QUEUE = "request_queue"
CLUSTER_NODE_SET = "locust_nodes"


##
#  slave options
##

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.116 Chrome/48.0.2564.116 Safari/537.36"
CONCURRENCY = 16
STATUS_WATCHER_FRENQUENCY = 5  # seconds


