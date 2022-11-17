from __future__ import annotations

from requests import Session

from datetime import datetime
import json
from typing import Tuple, List, Self
import socket
from random import choice
from statistics import mean
from threading import Thread
from time import sleep, time
import sys
import subprocess
from itertools import cycle
from functools import cache


from util.custom_requests import RequestManager
from custom_logger import Logger as log, Color as c
from util.utils import *
from util.calculate_droptime import get_starshopping_dt
from util.errors import *

class Sniper:
    def __init__(self, target, offset) -> None:
        self.target: str = target
        self.offset: float = float(offset)
        self.accounts: List[MicrosoftAccount] = parse_accounts()
        self.session: RequestManager = RequestManager(Session())
        
        self.droptime: int = get_starshopping_dt(target)
        self.authenticated = False
        
        self._success = ()
        
        self.threads: List[Thread] = []
        self.socks: List[socket.socket] = [create_socket() for _ in range(len(self.accounts)*3)]
        self.socks_setup = False
        
        self.debug = False
        self.fancy_timer, self.skinchange, self.skin_variant, self.skin_url = self.parse_json()
        
        self.skin_change_result = None

            
    @cache
    def fancy_countdown_time(self, count: int) -> None:
        if self.debug:
            count=15
        
        for count in range(int(count), 0, -1):
            minutes, seconds = divmod(count, 60)
            if minutes > 59:
                hours, minutes = divmod(minutes, 60)
                log.info(f"{c.magenta}Sniping {self.target} in ~~ {'0' if hours < 10 else ''}{hours}:{'0' if minutes < 10 else ''}{minutes}:{'0' if seconds < 10 else ''}{seconds}😴😴", _end="\r")
            elif minutes:
                log.info(f"{c.magenta}Sniping {self.target} in ~~ {'0' if minutes < 10 else ''}{minutes}:{'0' if seconds < 10 else ''}{seconds}🙄🙄   ", _end="\r")
            else:
                log.info(f"{c.magenta}Sniping {self.target} in ~~ {seconds}s! 🚀🚀   ", _end="\r")
                if seconds <= 30 and self.authenticated == False:
                    Thread(target=self.authenticate).start()
                elif seconds == 0:
                    break
                
                elif seconds == 10:
                    Thread(target=self.setup_sockets).start()
            sleep(1)
            count -=1
        return
    
    @cache
    def accurate_timer(self) -> None:
        while (count := self.droptime - time()-self.offset/1000) > 0:
            sleep(0.1)
            log.info(f"Sniping {self.target} in {datetime.utcfromtimestamp(int(count)).strftime('%H:%M:%S')}      ", _end="\r")
            if int(count) <= 30 and not self.authenticated:
                Thread(target=self.authenticate).start()
                
            if int(count) <= 10 and not self.socks_setup:
                Thread(target=self.setup_sockets).start()
    
    def snipe(self) -> None:
        log.success(f"{c.magenta} {len(self.accounts)} account chosen...\n")

        # The generally more inaccurate timer
        if self.fancy_timer:
            self.fancy_countdown_time((self.droptime - time()-self.offset/1000))
            
        # more accurate timer
        else:
            self.accurate_timer()
                
                
                
        
        for thread in self.threads:
            thread.start()
            
        for thread in self.threads:
            thread.join()
            
        log.info(f"{c.green}Terminating threads...")
        terminate_threads()
        if self.debug:
            self._success = (True, self.accounts[0].bearer)
        success_or_fail_message = self.success()
        
        sleep(1)
        log.info(f"{success_or_fail_message}")
        exit = log.yes_or_no(f"{c.red}Would you like to exit (yes/no)")
        
        if exit:
            self.session.session.close()
            sys.exit()
            
        self.session.session.close()
            

    def _snipe(self, account: MicrosoftAccount, sock: socket.socket) -> bool | Tuple[bool, MicrosoftAccount.returnBearer]:
        # Send data
        sock.send(bytes(f"PUT /minecraft/profile/name/{self.target} HTTP/1.1\r\nHost: api.minecraftservices.com\r\nAuthorization: Bearer " + f"{account.bearer}\r\n\r\n", 'utf-8'))
        
        # recive data
        data = sock.recv(2048).decode('utf-8')
        recv = time()
        
        # close socket
        sock.close()
        
        # status code
        try:
            status = int(data.split('Content-Type')[0].rstrip()[8:12].rstrip())
        except ValueError:
            log.error(f"{c.red}Request failed")
            
        if status in (200, 203):
            sys.stdout.write(f"{c.cyan}[{c.l_green}{status}{c.cyan}] ~ :))\n")
            sys.stdout.flush()
            self._success = (True, account.bearer)
            
        elif recv - self.droptime < 0.01:
            sys.stdout.write(f"{c.l_yellow}[{c.magenta}{status}{c.l_yellow}] {c.l_yellow}Early by {abs(round((recv - self.droptime - 0.01)*10000))/10}ms\n")
            sys.stdout.flush()
            
        elif recv - self.droptime > 0.02:
            sys.stdout.write(f'{c.l_yellow}[{c.magenta}{status}{c.l_yellow}] {c.l_red}Late by {round((recv - self.droptime - 0.02)*10000)/10}ms\n')
            sys.stdout.flush()
            
        elif status >= 500:
            sys.stdout.write(f'{c.l_yellow}[{c.magenta}{status}{c.l_yellow}] {c.l_red}Lagged :((\n')
            sys.stdout.flush()
            
        else:
            pass
            
            
    def success(self) -> str:
        if not any(self._success):
            return f"{c.red}Failed to snipe {self.target} :("
        
        for account in self.accounts:
            if not (email := account._get_email_on_success((bearer := self._success[1]))):
                continue
            
            log.info(f"{c.red}Succesfully Sniped {c.cyan}{self.target} onto {c.l_green}{email}!")
            if self.skinchange:
                Thread(target=self.skin_change, args=(bearer,)).start()
                
                # fancy fake loading screen :D
                while self.skin_change_result is None:
                    for loading_symbol in cycle(['|', '/', '-', '\\']):
                        print(f"{c.l_magenta}Changing skin: {c.yellow}{loading_symbol}", end="\r", flush=True)
                        sleep(0.1)
                        if self.skin_change_result != None:
                            break
                
                if self.skin_change_result in (200, 203):
                    log.success(f"{c.l_green}Successfuly changed skin: {self.skin_change_result}✔️")
                    
                else:
                    log.error(f"{c.red}Failed to change skin: {self.skin_change_result}❌")

                                 
        return f"{c.l_green}Congrats on sniping {self.target}!\n" if self.skinchange == True else f"{c.l_green}Congrats on sniping {self.target}!"
    
    def setup_sockets(self) -> None:
        self.socks_setup = True
        for sock_ in self.socks:
            sock_.connect(('api.minecraftservices.com', 443))
            self.threads.append(Thread(target=self._snipe, args=(choice(self.accounts), wrap_socket(sock_))))
            

        log.success("Generated snipe threads..")
        
    def authenticate(self) -> None:
        self.authenticated = True
        _authenticate_thread = [Thread(target=account._authenicate_account, args=(self.session.session,)) for account in self.accounts]
        [thread.start() for thread in _authenticate_thread]
        if sys.platform == "win32":
            subprocess.run('cls', shell=True)
            banner()
        else:
            subprocess.run('clear')
            banner()
            
    def parse_json(self) -> None:
        with open('../pandora.json', mode='r') as f:
            config = json.load(f)
            return config['fancy_timer'], config['skin_change'], config['skin_variant'], config['skin_url']
        
    def skin_change(self, bearer) -> None:
        sleep(5)
        status, json_, resp = self.session.post(
                    "https://api.minecraftservices.com/minecraft/profile/skins",
                        headers={
                                "Authorization": f"Bearer {bearer}",
                                 "Content-Type": "application/json"
                                 },
                            json={
                                "url": f"{self.skin_url}",
                                  "variant": f"{self.skin_variant}"
                                  }
                            )
        self.skin_change_result = status
        
    def __repr__(self) -> Self:
        return self
        
            
    
def banner() -> None:
    print(f"""{c.magenta}
            \t\t _ (`-.    ('-.         .-') _  _ .-') _               _  .-')     ('-.     
 \t\t ( (OO  )  ( OO ).-.    ( OO ) )( (  OO) )             ( \( -O )   ( OO ).-. 
 \t\t_.`     \  / . --. /,--./ ,--,'  \     .'_  .-'),-----. ,------.   / . --. / 
\t\t(__...--''  | \-.  \ |   \ |  |\  ,`'--..._)( OO'  .-.  '|   /`. '  | \-.  \  
 \t\t|  /  | |.-'-'  |  ||    \|  | ) |  |  \  '/   |  | |  ||  /  | |.-'-'  |  | 
 \t\t|  |_.' | \| |_.'  ||  .     |/  |  |   ' |\_) |  |\|  ||  |_.' | \| |_.'  | 
 \t\t|  .___.'  |  .-.  ||  |\    |   |  |   / :  \ |  | |  ||  .  '.'  |  .-.  | 
 \t\t|  |       |  | |  ||  | \   |   |  '--'  /   `'  '-'  '|  |\  \   |  | |  | 
 \t\t`--'       `--' `--'`--'  `--'   `-------'      `-----' `--' '--'  `--' `--' 
          """)

if __name__ == "__main__":
    while True: 
        if sys.platform == "win32":
            subprocess.run('cls', shell=True)
            banner()
        else:
            subprocess.run('clear')
            banner()
        target = log.input(f"{c.blue}Target name ~").rstrip()
        if len(target) < 3:
            log.error(f"{c.red}Invalid Username")
            continue
        offset = log.yes_or_no(f"{c.l_yellow}Auto Offset? ~")
        if offset:
            from util.auto_offset import *
                
            offset = mean([ping(3) for _ in range(3)])
            log.info(f"{c.l_magenta}Offset ~ {c.l_green}{offset}ms")
                
        else:
            offset = log.input(f"{c.cyan}Offset ~")
            
        s = Sniper(target, offset)
        s.snipe()