from __future__ import annotations

from typing import List
import threading
from time import sleep
import socket
import ssl

from util.classes.Account import MicrosoftAccount
from custom_logger import Logger as log, Color as _
from .errors import InvalidAccounts

class Socket:
    pass

def parse_accounts() -> List[MicrosoftAccount]:
    accounts = []
    try: 
        with open('accounts.txt') as file:
            for idx, line in enumerate(file.read().splitlines()):
                if not line.strip():
                    continue
                
                split_co = line.split(':')
                
                if len(split_co) != 2:
                    log.error(f"{_.red}Invalid account at line {idx+1} in accounts.txt")
                    continue
                
                email, password = split_co[0], split_co[1]
                
                accounts.append(MicrosoftAccount(
                    email,
                    password
                ))
    except FileNotFoundError:
        log.error(f"{_.red}accounts.txt does not exsist!")
        return False
                
    if len(accounts) < 1:
        log.error(f"{_.red}All of your accounts were entered incorrectly")
        raise InvalidAccounts(
            message="None of your accounts were formatted correctly"
        )
    log.success(f"{_.l_green}Succesfully loaded accounts")
    return accounts


def terminate_threads() -> None:
    threads = threading.active_count() - 1
    while threads:
        threads = threading.active_count() - 1
        sleep(0.5)
        
def create_socket() -> Socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return sock

def wrap_socket(sock) -> Socket:
    sock_ = ssl.create_default_context().wrap_socket(sock, server_hostname='api.minecraftservices.com')
    return sock_

