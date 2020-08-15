import hashlib
import json
import time


def calc_hash(s):
    return hashlib.sha512(json.dumps(s).encode()).hexdigest()[:8] + "..."
    # return hashlib.sha512(json.dumps(s).encode()).hexdigest()


def get_time():
    return int(time.time() * 1000000)
    # return time.time_ns() # not available until 3.7
