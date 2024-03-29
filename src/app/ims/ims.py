import json
import time
import os
from dataclasses import dataclass
from typing import Dict
from dotenv import load_dotenv
import requests
from dataclasses_json import dataclass_json

load_dotenv()
ims_url = 'ims-na1-stg1.mycompanylogin.com'
ims_org_id = os.environ.get('IMS_ORG_ID')
ims_client_id =  os.environ.get('IMS_CLIENT_ID')
ims_client_secret = os.environ.get('IMS_CLIENT_SECRET')
ims_auth_code = os.environ.get('IMS_AUTH_CODE')

def load_credentials():
    client_id = ims_client_id
    client_secret = ims_client_secret
    client_code = ims_auth_code
    return ServiceClientCredentials(client_id, client_secret, client_code)

@dataclass_json
@dataclass
class ServiceClientCredentials:
    client_id: str
    client_secret: str
    client_code: str


class TokenProvider:
    _ims_stage_url = 'https://ims-na1-stg1.mycompanylogin.com/ims/token/v2'
    _ims_prod_url = 'https://ims-na1.mycompanylogin.com/ims/token/v2'

    def __init__(self, creds: ServiceClientCredentials, stage=False):
        if stage:
            self.ims_url = self._ims_stage_url
        else:
            self.ims_url = self._ims_prod_url
        self.creds = creds
        self._service_token = None
        self._service_token_expiry = 0
        self._service_token_expiry_buffer = 5 * 60 * 60  # 5 minutes

    def _generate_service_token(self) -> Dict:
        params = {
            'client_id': self.creds.client_id,
            'client_secret': self.creds.client_secret,
            'code': self.creds.client_code,
            'grant_type': 'authorization_code',
        }
        response = requests.post(self.ims_url, data=params)
        response_dict = json.loads(response.text)
        return response_dict

    def _get_service_token(self) -> str:
        regen_token = False
        if self._service_token is None:
            regen_token = True
        if time.time() > self._service_token_expiry - self._service_token_expiry_buffer:
            regen_token = True

        if regen_token:
            token_dict = self._generate_service_token()
            self._service_token = token_dict['access_token']
            self._service_token_expiry = time.time() + token_dict['expires_in']
            return self._service_token
        return self._service_token

    def get_token(self):
        return self._get_service_token()

    def get_client_id(self):
        return self.creds.client_id