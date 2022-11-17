from __future__ import annotations

import requests
import socket
from datetime import datetime
from time import time, sleep



def get_starshopping_dt(target: str) -> int or bool:
    resp = requests.get(
        "https://api.star.shopping/droptime/%s" % (target),
                        headers={"User-Agent": "Sniper"})
    try:
        unix_time = int(resp.json()['unix'])
    except KeyError:
        # print(
        # f"Could not fetch the droptime for {target}{target}"
        # " perhaps the name is avaliable?")
        # raise NameNotDropping(
        #     message=f"{target} is not dropping"
        # )
        raise KeyError(f"{target} not dropping")
        pass
    
    
    print(
            f"{target} is dropping @ {datetime.fromtimestamp(unix_time)}"
            )

        
    return unix_time


def _get_starshoppingdt(target: str) -> int | bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect(('api.star.shopping', 80))
    sock.send(bytes(f"GET /droptime/{target} HTTP/1.1\r\nHost: api.star.shopping\r\nUser-Agent: Sniper\r\n\r\n", 'utf-8'))

    data = sock.recv(800).decode('utf-8')
    try:
        data = data.split('unix')[1]
        unix_time = int("".join(char for char in data if char.isdigit()))
    except IndexError:
        # log.error(
        # f"{c.red}Could not fetch the droptime for {target}{c.l_magenta}"
        # " perhaps the name is avaliable?")
        # raise NameNotDropping(
        #     message=f"{target} is not dropping"
        # )
        raise IndexError(f'{target} not dropping')
        pass
        
    print(
            f"{target} is dropping @ {datetime.fromtimestamp(unix_time)}"
            )
        
    return unix_time

start = time()
unix = _get_starshoppingdt('ham') # change to any name that is dropping
print(unix)
end_sockets = time()-start
sleep(5)
start=time()
unix = get_starshopping_dt('ham')
end_requests =time()-start

if end_sockets < end_requests:
    print("sockets was faster than requests")
else:
    print('requests was faster than sockets')
    
# In conclusion, 100% of the time sockets was faster than requests for grabbing droptime
    
    
    

