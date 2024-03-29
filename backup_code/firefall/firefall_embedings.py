import os
from typing import List, Any, Dict
import http
import json
import time, logging
from auth.ims import get_ims_access_token, ims_client_id, ims_org_id

emerald_url = os.environ.get("emerald_url" ,"emerald-stage.mycompany.io")
# openai-embedder vs openai-embedder-2
emerald_embedder_id = os.environ.get("emerald_embedder_id", "openai-embedder")


def firefall_get_embeddings(text) -> List[float]:  
    conn = http.client.HTTPSConnection(emerald_url)

    asset_type = "text"
    input_format = "text"

    payload_dict = {
        "embedder_id": emerald_embedder_id,
        "asset_type": asset_type,
        "input_format": input_format,
        "data": text
    }

    # Convert the dictionary to a JSON string
    payload = json.dumps(payload_dict)
    token = get_ims_access_token()
    print(token)
      
    
    headers = {
        'x-api-key': ims_client_id,
        'x-gw-ims-org-id': ims_org_id,
        'Authorization': "Bearer " + token,
    }

    try:
        start_time = time.time()
        conn.request("POST", "/embedding?=", payload, headers)
        res = conn.getresponse()
        if res.status != 200:
            raise Exception(f"Error: {res.status} {res.reason}")
        data = res.read()
        end_time = time.time()
        elasped_time = end_time - start_time
        logging.debug(f"Got embeddings in {elasped_time} seconds")
        return json.loads(data.decode("utf-8"))["vector"]
    except Exception as e:
        logging.error(f"Got Emerald Error: {e}")
        raise Exception(f"Got Emerald Error: {e}")
    