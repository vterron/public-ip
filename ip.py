#! /usr/bin/env python3

import collections
import random
import requests
import threading
from queue import Queue

URLS = [
    'http://api.ipify.org',
    'http://checkip.amazonaws.com',
    'http://icanhazip.com/',
    'http://ifconfig.co/ip',
    'http://ipecho.net/plain',
    'http://ipinfo.io/ip',
]

NURLS = 5  # Number of websites to query.

def _get_ip(url, queue, timeout):
    """Get external IP from 'url' and put it into 'queue'."""

    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        ip = r.text.strip()
        print(url, "->", ip)
        queue.put(ip)
    except (requests.exceptions.HTTPError,
            requests.exceptions.Timeout):
        return None


def get(nurls=len(URLS), timeout=0.25):
    """"Returns the current external IP."""

    threads = []
    queue = Queue()
    for url in random.sample(URLS, nurls):
        t = threading.Thread(target=_get_ip, args=(url, queue, timeout))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    ips = []
    while not queue.empty():
        ips.append(queue.get())
    return collections.Counter(ips).most_common(1)[0][0]


if __name__ == "__main__":
    print("IP: ", get())
