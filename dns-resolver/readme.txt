DNS-resolver by Skipper95 a.k.a Egor Bushmelev

usage: dnsresolve.py [-h] [--server [Server]] [--port [Port]] [-d] [-n [NUM]]
                     [-w [WAITING]]
                     Address [Address ...]

positional arguments:
  Address               Address that you need to resolve

optional arguments:
  -h, --help            show this help message and exit
  --server [Server], -s [Server]
                        Set the DNS server to first request, default: 8.8.8.8
  --port [Port], -p [Port]
                        Set the port of dedicated DNS server
  -d, --debug           switch on debug mode
  -n [NUM], --num [NUM]
                        number of retries
  -w [WAITING], --waiting [WAITING]
                        waiting time of request

example: dnsresolve -s 8.8.8.8 -p 53 -d -n 4 -w 2 google.com
