from __future__ import annotations

from requests import Session


class RequestManager:
    def __init__(self, session) -> None:
        self.session: Session = session
        
    def get(self, *args, **kwargs):
        with self.session.get(*args, **kwargs) as response:
            try:
                respjson = response.json()
            except Exception:
                respjson = None
                
            return response.status_code, respjson, response 
        
    def post(self, *args, **kwargs) -> None:
        with self.session.post(*args, **kwargs) as response:
            try:
                respjson = response.json()
            except Exception:
                respjson = None
                
            return response.status_code, respjson, response 
        
    def put(self, *args, **kwargs) -> None:
        with self.session.put(*args, **kwargs) as response:
            try:
                respjson = response.json()
            except Exception:
                respjson = None
                
            return response.status_code, respjson, response 