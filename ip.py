#! /usr/bin/env python3

import collections
import random
import requests
import threading
import queue

URLS = [
    'http://api.ipify.org',
    'http://checkip.amazonaws.com',
    'http://icanhazip.com/',
    'http://ifconfig.co/ip',
    'http://ipecho.net/plain',
    'http://ipinfo.io/ip',
]

NURLS = 5  # Number of websites to query.

q = queue.Queue()

def get_ip(url, timeout=0.25):
   r = requests.get(url, timeout=timeout)
   try:
       r.raise_for_status()
       ip = r.text.strip()
       print(url, "->", ip)
       q.put(ip)
   except (requests.exceptions.HTTPError,
           requests.exceptions.Timeout):
       return None


if __name__ == "__main__":

    threads= []
    for url in random.sample(URLS, NURLS):
        t = threading.Thread(target=get_ip, args=(url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    ips = []
    while not q.empty():
        ips.append(q.get())
    print("IP: ", collections.Counter(ips).most_common(1)[0])


    # Serial version
    #ips = []
    #for url in URLS:
    #    ips.append(get_ip(url))
    #    print(url, "->", ips[-1])
    #print()
    #print("IP: ", collections.Counter(ips).most_common(1)[0])
