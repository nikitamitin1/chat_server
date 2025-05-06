import time, redis, uuid
r = redis.Redis("localhost", 6379)

ONLINE_TTL = 45       # seconds
CHECK_INTERVAL = 15   # how often we re‑scan

def mark_online(user_id: uuid.UUID):
    r.set(f"online:{user_id}", 1, ex=ONLINE_TTL)

def presence_sweeper():
    while True:
        now = int(time.time())
        # Redis handles expiry automatically; optionally,
        # build list of online users per chat for analytics.
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    presence_sweeper()
