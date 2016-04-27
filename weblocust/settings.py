#coding:utf-8
CONCURRENCY = 16
REDIS_SERVER = "localhost"
MASTER_ADDRESS = "10.0.0.100"

REQUEST_QUEUE = "request_queue"
CLUSTER_NODE_SET = "locust_nodes"

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.116 Chrome/48.0.2564.116 Safari/537.36"

NODE_ROLE = "master" # master or slave

DETECT_ZOMBIE_FRENQUENCY = 10  # seconds