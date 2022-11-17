from __future__ import annotations

import requests
from datetime import datetime
from .errors import NameNotDropping

from custom_logger import Logger as log, Color as c


def get_starshopping_dt(target: str) -> int:
    get_unix = requests.get(f"https://api.star.shopping/droptime/{target}",
                             headers={"User-Agent": "Sniper"})
    try:
        unix_time = get_unix.json()['unix']
    except KeyError:
        log.error(
        f"{c.red}Could not fetch the droptime for {target}{c.l_magenta}"
        " perhaps the name is/isn't avaliable?")
        raise NameNotDropping(
            message=f"{target} is not dropping"
        )
        
    log.info(
            f"{target} is dropping @ {datetime.fromtimestamp(unix_time)}"
            )
        
    return unix_time
