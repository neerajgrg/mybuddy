import asyncio
import datetime
import json
import time
from typing import Dict
from dataclasses import dataclass

import aiohttp
import requests
import tiktoken
from dataclasses_json import dataclass_json
from app.ims.ims import TokenProvider

class FireFallRequestBuilder:
    _stage_url = 'https://firefall-stage.mycompany.io'
    _prod_url = 'https://firefall.mycompany.io'

    def __init__(self):
        self.token_provider = None
        self.creds = None
        self.url = None
        self.ims_url = None
        self.llm_metadata = {
            "model_name": "text-davinci-003",
            "temperature": 0.2,
            "max_tokens": 200,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "n": 1,
            "best_of": 1
        }
        self.timeout = 60

    def set_timeout(self, timeout):
        self.timeout = timeout
        return self

    def set_env(self, stage=False, prod=False):
        # default to stage
        is_stage = stage or not prod
        if is_stage:
            self.url = self._stage_url
        else:
            self.url = self._prod_url
        return self

    def set_token_provider(self, provider):
        self.token_provider = provider
        return self

    def set_model(self, model):
        self.llm_metadata['model_name'] = model
        if model in ['gpt-4', 'gpt-4-32k', 'gpt-35-turbo']:
            self.llm_metadata['llm_type'] = 'azure_chat_openai'
            del self.llm_metadata['best_of']
        else:
            self.llm_metadata['llm_type'] = 'azure_openai'
        return self

    def set_temperature(self, temperature):
        self.llm_metadata['temperature'] = temperature
        return self

    def set_max_tokens(self, tokens):
        self.llm_metadata['max_tokens'] = tokens
        return self

    def build(self):
        return FireFallRequest(self.url, llm_metadata=self.llm_metadata, token_provider=self.token_provider,
                               timeout=self.timeout)


@dataclass_json
@dataclass
class FirefallResponse:
    response: str
    conversation_id: str
    query_id: str
    llm_output: dict


class FireFallRequest:
    _token_limits = {
        "gpt-35-turbo": 4096,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "text-davinci-003": 4096
    }

    _token_encoders = {
        "gpt-35-turbo": "cl100k_base",
        "gpt-4": "cl100k_base",
        "gpt-4-32k": "cl100k_base",
        "text-davinci-003": "p50k_base"
    }

    @classmethod
    def available_tokens(cls, query, model_name, max_tokens):
        if model_name not in cls._token_limits:
            print(f'Warning: {model_name} not in token limit map. Returning max tokens.')
            return max_tokens

        if model_name not in cls._token_encoders:
            raise ValueError(f'No token encoder for {model_name}')

        encoder = tiktoken.get_encoding(cls._token_encoders[model_name])
        tokens = len(encoder.encode(query))

        # 8 extra tokens are added on top of our query
        available_tokens = cls._token_limits[model_name] - tokens - 8
        return available_tokens

    def __init__(self, url, llm_metadata, token_provider: TokenProvider, timeout=60):
        self.url = url
        self.token_provider = token_provider
        self.llm_metadata = llm_metadata
        self.timeout = timeout

    @staticmethod
    def builder() -> FireFallRequestBuilder:
        return FireFallRequestBuilder()

    async def completions_async(self, query):
        model_name = self.llm_metadata['model_name']
        max_tokens = self.llm_metadata['max_tokens']
        available_tokens = self.available_tokens(query, model_name, max_tokens)
        if available_tokens < max_tokens:
            self.llm_metadata['max_tokens'] = available_tokens

        data = {
            'llm_metadata': self.llm_metadata,
            'dialogue': {
                'question': query
            }
        }
        start_time = datetime.datetime.utcnow()
        response = await self.invoke_async(self.url + '/v1/completions', data)
        end_itme = datetime.datetime.utcnow()

        response_dict = json.loads(response)
        conversation_id = response_dict['conversation_identifier']
        firefall_query_id = response_dict['query_id']
        llm_output = response_dict['llm_output']
        tokens = llm_output['token_usage']['total_tokens']
        text = response_dict['generations'][0][0]['text']

        result = FirefallResponse(text, conversation_id, firefall_query_id, llm_output)

        # # trace for later use
        # tracer: QueryTracer = current_tracer()
        # if tracer is not None:
        #     tracer.log_llm_request(
        #         query,
        #         self.llm_metadata['model_name'],
        #         result.response,
        #         tokens,
        #         (end_itme - start_time).total_seconds(),
        #         self.llm_metadata['temperature']
        #     )
        return result

    def _create_conversation(self, name='test_conversation'):
        azure_url = f'{self.url}/v2/conversation'
        payload = {
            "conversation_name": f"{name}",
            "capability_name": "open ai direct firefall api",
        }
        response = self.invoke(azure_url, payload)
        return int(json.loads(response)['conversation_id'])

    async def invoke_async(self, url, data=None, method='POST'):
        start = time.time_ns()
        retry_count = 0

        async with aiohttp.ClientSession() as session:
            while retry_count < 2:
                try:
                    headers = {
                        'x-gw-ims-org-id': self.token_provider.get_client_id(),
                        'x-api-key': self.token_provider.get_client_id(),
                        'Authorization': f'Bearer {self.token_provider.get_token()}',
                        'Content-Type': 'application/json',
                    }
                    async with session.post(url, headers=headers, json=data, timeout=self.timeout) as response:
                        print(response.status)
                        if response.status >= 400:
                            # handle frequent firefall failures
                            query = data.get('dialogue', {}).get('question', '')
                            print('received failure from firefall')
                            print(query)
                            return json.dumps({'error': True, 'status': response.status, 'text': await response.text()})
                        return await response.text()
                except asyncio.TimeoutError:
                    retry_count += 1
                    continue
        return json.dumps({'error': True, 'status': 500, 'text': 'timeout'})