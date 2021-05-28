A Python function to get your public IP address.

# Installation

```bash
pip install public-ip
```

# Usage example

```python
import public_ip as ip

ip.get()
```

Sample output:

```
212.51.139.31
```

# How it works

The function queries in parallel six different websites...

1. https://api.ipify.org
1. https://checkip.amazonaws.com
1. https://icanhazip.com
1. https://ifconfig.co/ip'
1. https://ipecho.net/plain
1. https://ipinfo.io/ip

... and returns the most common IP among the responses. This approach seeks to ensure that (a) we don't depend on a single external service and (b) we can determine the IP correctly as long as a _majority_ of these sites return the right value.