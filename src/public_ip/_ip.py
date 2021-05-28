#! /usr/bin/env python3

import collections
import logging
import random
import requests
import threading
from queue import Queue

URLS = [
    'https://api.ipify.org',
    'https://checkip.amazonaws.com',
    'https://icanhazip.com',
    'https://ifconfig.co/ip',
    'https://ipecho.net/plain',
    'https://ipinfo.io/ip',
]

NURLS = 5  # Number of websites to query.

def _get_ip(url, queue, timeout):
    """Get external IP from 'url' and put it into 'queue'."""

    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        ip = r.text.strip()
        logging.info("Asked %s for our IP -> %s", url, ip)
        queue.put(ip)
    except (requests.exceptions.HTTPError,
            requests.exceptions.Timeout):
        return None


def get(nurls=len(URLS), timeout=0.25):
    """"Returns the current external IP.

    Launches 'nurls' processes in parallel, each one of them fetching the
    external IP from one of the websites in the URLS module-level variable.
    Each independent request timeouts after 'timeout' seconds. After all of
    them have completed, returns the most common IP. In this manner we will
    return the correct IP as long as the majority of URLs we talk to report
    our actual IP.
    """

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
