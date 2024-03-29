
import http.client
import json
import logging
import os

from app.ims.ims import ims_auth_code, ims_client_id, ims_client_secret, ims_org_id, ims_url, get_ims_access_token

firefall_url = os.environ.get("firefall_url" ,"firefall-stage.mycompany.io")

def firefall_get_completions(prompt, stop=["\\n", "\\t"]) -> str:
    logging.debug('firefall_get_completions()')
    conn = http.client.HTTPSConnection(firefall_url)

    model_name = "gpt-35-turbo"
    temperature = 0.1
    max_tokens = 3000
    top_p = 1.0
    frequency_penalty = 0
    presence_penalty = 0.9
    n = 1
    llm_type = "azure_chat_openai"

    # Define the payload as a dictionary
    payload_dict = {
        "dialogue": {
            "question": prompt
        },
        "llm_metadata": {
            "model_name": model_name,
            "temperature": temperature,
            # "max_tokens": max_tokens,
            # "top_p": top_p,
            # "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "n": n,
            "llm_type": llm_type,
            "stop": stop
        }
    }

    payload = json.dumps(payload_dict, indent=4)

    headers = {
        'x-api-key': ims_client_id,
        'x-gw-ims-org-id': ims_org_id,
        'Authorization': "Bearer " + get_ims_access_token(),
    }

    conn.request("POST", "/v1/completions?=", payload, headers)

    res = conn.getresponse()
    if res.status != 201:
        res_content = res.read().decode('utf-8')
        try:
            res_json = json.loads(res_content)
            error_text = res_content
            if "detail" in res_json and "error_message" in res_json["detail"]:
                error_text = res_json["detail"]["error_message"]
            else:
                error_text = res_content
        except:
            error_text = res_content

        logging.error(f"Got Firefall Error: {res.status} {res.reason} \n {error_text}")
        # raise HTTPException(status_code=500, detail=error_response)
        raise Exception(f"Error: {res.status} {res.reason} \n {error_text}")
    completions = json.loads(res.read().decode("utf-8"))

    logging.debug(f"Got Firefall response: {completions}")
    return completions["generations"][0][0]["text"]
