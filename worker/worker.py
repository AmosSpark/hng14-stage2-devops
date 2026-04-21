import redis
import time
import os
import signal

r = redis.Redis(host=os.environ["REDIS_HOST"], port=int(os.environ["REDIS_PORT"]), password=os.environ["REDIS_PASSWORD"])

running = True

def shutdown(signum, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

def process_job(job_id):
    print(f"Processing job {job_id}")
    r.hset(f"job:{job_id}", "status", "processing")
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")

while running:
    try:
        job = r.brpop("jobs", timeout=5)
        if job:
            _, job_id = job
            process_job(job_id.decode())
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)
