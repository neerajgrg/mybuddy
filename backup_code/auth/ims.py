import logging
import http.client
import urllib.parse
import json
import os
from dotenv import load_dotenv

from cachetools import cached, TTLCache

from app.ims.ims import ServiceClientCredentials

load_dotenv()

ims_url = 'ims-na1-stg1.mycompanylogin.com'
ims_org_id = os.environ.get('IMS_ORG_ID')
ims_client_id =  os.environ.get('IMS_CLIENT_ID')

ims_client_secret = os.environ.get('IMS_CLIENT_SECRET')
ims_auth_code = os.environ.get('IMS_AUTH_CODE')

access_token_cache = TTLCache(maxsize=100, ttl=300)


def load_credentials():
    client_id = ims_client_id
    client_secret = ims_client_secret
    client_code = ims_auth_code
    return ServiceClientCredentials(client_id, client_secret, client_code)

# def get_tokens():
#     logging.debug(
#         f"Asking for a new token from ims_url: {ims_url} with client_id: {ims_client_id} imsOrgId: {ims_org_id}")
    
#     conn = http.client.HTTPSConnection(ims_url)

#     headers = {
#       'Content-Type': 'application/x-www-form-urlencoded'
#     }

#     grant_type = "authorization_code"
#     query_string = f"/ims/token/v4"

#     data = {
#         'grant_type': f"{grant_type}",
#         'client_id': f"{ims_client_id}",  # Replace with your actual client ID
#         'client_secret': f"{ims_client_secret}",      # Replace with your actual client secret
#         'code': f"{ims_auth_code}"                # Replace with the actual code received from the authorization request
#     }

#     params = urllib.parse.urlencode(data).encode()
    
#     conn.request("POST", query_string, params, headers)

#     res = conn.getresponse()
#     data = res.read()
#     result = json.loads(data.decode("utf-8"))
#     logging.debug(f"Got new token")
#     print(result)

#     return result

# @cached(access_token_cache)
# def get_ims_access_token():
#     return get_tokens()["access_token"]