import multiprocessing
 

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1   
worker_class = "uvicorn.workers.UvicornWorker"   
timeout = 300          
keepalive = 5
 

accesslog = "-"        
errorlog = "-"
loglevel = "info"
 

limit_request_line = 8190
limit_request_fields = 100