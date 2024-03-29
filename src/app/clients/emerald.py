# mycompany CONFIDENTIAL
# ___________________
#
#  Copyright 2023 mycompany Systems Incorporated
#  All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains
# the property of mycompany Systems Incorporated and its suppliers,
# if any.  The intellectual and technical concepts contained
# herein are proprietary to mycompany Systems Incorporated and its
# suppliers and are protected by all applicable intellectual property
# laws, including trade secret and copyright laws.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from mycompany Systems Incorporated.
import asyncio
import json
import time
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List


from app.ims.ims import TokenProvider
import aiohttp


class EmeraldRequestBuilder:
    _stage_url = 'https://emerald-stage.mycompany.io'
    _prod_url = 'https://emerald.mycompany.io'  # emerald not available on prod yet.

    def __init__(self):
        self.token_provider = None
        self.creds = None
        self.url = None
        self.ims_url = None
        self.timeout = 60
        self.embedder = "openai-embedder"

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

    def set_embedder(self, embedder):
        self.embedder = embedder
        return self

    def build(self):
        return EmeraldRequest(self.url, token_provider=self.token_provider, timeout=self.timeout)


class EmeraldRequest:
    def __init__(self, url, token_provider: TokenProvider, timeout=60):
        self.url = url
        self.token_provider = token_provider
        self.timeout = timeout

    @staticmethod
    def builder() -> EmeraldRequestBuilder:
        return EmeraldRequestBuilder()

    async def search_asset(self, query, collection_name, top_n, threshold=0.0):
        """
        Searching asset in the collection based on the query
        """

        data = {
            "input_format": "text",
            "data": query,
            "top_n": top_n,
            "threshold": threshold
        }

        response = await self.invoke(self.url + '/collection/' + collection_name + '/search', data)

        asset_id = [i.get("asset_id", "") for i in json.loads(response)]

        return asset_id

    async def get_asset_by_id(self, asset_ids, collection_name):
        """
        Getting asset based on Asset ID
        """
        pending = []
        for asset_id in asset_ids:
            promise = self.invoke(self.url + '/collection/' + collection_name + '/asset/' + asset_id, data={},
                                  method="get")
            pending.append(promise)
        assets = await asyncio.gather(*pending)
        assets = [json.loads(i) for i in assets]
        return assets

    async def invoke(self, url, data, method="post"):
        if url.startswith("/"):
            url = self.url + url
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
                    async with session.request(method, url, headers=headers, json=data,
                                               timeout=self.timeout) as response:
                        if response.status >= 400:
                            print('received failure from emerald')
                            raise RuntimeError(f'Error from emerald: {response.status} text={await response.text()}')
                        return await response.text()
                except asyncio.TimeoutError:
                    retry_count += 1
                    continue
            raise RuntimeError(f'Error from emerald: {response.status}')


@dataclass_json
@dataclass
class Asset:
    data: str
    metadata: dict
    asset_id: str
    input_format: str = 'text'


class EmeraldClient:
    def __init__(self, token_provider: TokenProvider, is_stage=False):
        self.token_provider = token_provider
        self.is_stage = is_stage

    async def create_collection(self, collection_name, embedder='openai-embedder'):
        data = {"collection_name": collection_name, "asset_type": "text", "embedder_id": embedder}
        request = (
            EmeraldRequest.builder()
            .set_env(stage=self.is_stage)
            .set_token_provider(self.token_provider)
            .build()
        )
        response = await request.invoke('/collection', data)
        return response

    async def list_collections(self):
        request = (
            EmeraldRequest.builder()
            .set_env(stage=self.is_stage)
            .set_token_provider(self.token_provider)
            .build()
        )
        response = await request.invoke('/collection', data={}, method="get")
        return response
    
    async def get_collectionByName(self, collection_name: str):
        request = (
            EmeraldRequest.builder()
            .set_env(stage=self.is_stage)
            .set_token_provider(self.token_provider)
            .build()
        )
        response = await request.invoke('/collection/' + collection_name, data={}, method="get")
        return response

    async def delete_collection(self, collection_name: str):
        request = (
            EmeraldRequest.builder()
            .set_env(stage=self.is_stage)
            .set_token_provider(self.token_provider)
            .build()
        )
        response = await request.invoke('/collection/' + collection_name, data={}, method="delete")
        return response

    async def add_assets(self, collection_name: str, assets: List[Asset], override=True):
        request = (
            EmeraldRequest.builder()
            .set_env(stage=self.is_stage)
            .set_token_provider(self.token_provider)
            .build()
        )
        query = '?override=true' if override else ''
        response = await request.invoke('/collection/' + collection_name + '/asset' + query,
                                        data=[asset.to_dict() for asset in assets])
        return response
    
    async def list_assets(self, collection_name: str):
        request = (
            EmeraldRequest.builder()
            .set_env(stage=self.is_stage)
            .set_token_provider(self.token_provider)
            .build()
        )
        response = await request.invoke('/collection/' + collection_name + '/asset',
                                        data=[], method="get")
        return response
    
    async def get_asset(self, collection_name: str, asset_id: str):
        request = (
            EmeraldRequest.builder()
            .set_env(stage=self.is_stage)
            .set_token_provider(self.token_provider)
            .build()
        )
        asset_ids = [asset_id]
        assets = await request.get_asset_by_id(asset_ids, collection_name)
        if len(assets) > 0:
            return assets[0]
        return None
    
    def emerald_request(self):
        emerald_request = (
            EmeraldRequest.builder()
            .set_env(stage=self.is_stage)
            .set_token_provider(self.token_provider)
            .build()
        )
        return emerald_request