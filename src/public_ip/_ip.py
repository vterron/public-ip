#! /usr/bin/env python3

import collections
import logging
import random
import requests
import threading
import typing
from queue import Queue

URLS = [
    "https://api.ipify.org",
    "https://checkip.amazonaws.com",
    "https://icanhazip.com",
    "https://ifconfig.co/ip",
    "https://ipecho.net/plain",
    "https://ipinfo.io/ip",
]


def _get_ip(url: str, queue: Queue, timeout: float) -> None:
    """Get external IP from 'url' and put it into 'queue'."""

    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        ip = r.text.strip()
        logging.info("Asked %s for our IP -> %s", url, ip)
        queue.put(ip)
    except (requests.exceptions.HTTPError, requests.exceptions.Timeout):
        pass


def get(nurls: int = len(URLS), timeout: float = 1) -> str:
    """ "Returns the current external IP.

    Launches 'nurls' processes in parallel, each one of them fetching the
    external IP from one of the websites in the URLS module-level variable.
    Each independent request timeouts after 'timeout' seconds. After all of
    them have completed, returns the most common IP. In this manner we will
    return the correct IP as long as the majority of URLs we talk to report
    our actual IP.
    """

    threads = []
    queue: Queue = Queue()
    for url in random.sample(URLS, nurls):
        t = threading.Thread(target=_get_ip, args=(url, queue, timeout))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    ips = []
    while not queue.empty():
        ips.append(queue.get())

    if not ips:
        raise IOError("all server queries failed")

    # If there's a single IP among the responses, we're done.
    counter = collections.Counter(ips)
    if len(counter) == 1:
        return counter.most_common(1)[0][0]

    # Make sure there isn't a tie among the two most common IPs.
    top_two = counter.most_common(2)
    first_ip, first_votes = top_two[0]
    second_ip, second_votes = top_two[1]
    if first_votes == second_votes:
        raise ValueError(
            f"tie between {first_ip} and {second_ip} among the "
            "responses ({first_votes} occurrences each)"
        )
    return first_ip
