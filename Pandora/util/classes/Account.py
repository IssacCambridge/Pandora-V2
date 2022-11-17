from __future__ import annotations

from requests import Session


import util.msmcauth as msmcauth
from custom_logger import Logger as log

class MicrosoftAccount:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.session: Session = None
        self.bearer = self._get_bearer()
        self.uuid = None
        self.username = None
        
        
    def _authenicate_account(self, session) -> str:
        account = msmcauth.login(
            self.email,
            self.password,
            session)
        self.uuid = account.uuid
        self.username = account.username
        log.success(
                "Authenticated"
                 f" {self.email}\n"
                 )
        return self.bearer
    
    def _get_bearer(self) -> str:
        """This is used because we dont wont to create a list of threads at the same second that we're sending the requests \
            instead, we generate the threads before the name drops (Bearers expire every 24h at 2PM)

        Returns:
            str: Bearer token
        """
        return msmcauth.login(self.email, self.password, self.session).access_token
    
    def _get_email_on_success(self, bearer) -> str or bool:
        return self.email if self.bearer == bearer else False
    
    def returnBearer(self) -> str:
        """Avoid threading error"""
        return self.bearer
    