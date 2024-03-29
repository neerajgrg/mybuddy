import datetime
import json
import base64
from auth.ims import load_credentials
from app.ims.ims import TokenProvider
from app.clients.emerald import EmeraldClient, Asset

def generateEmbeddings():
    channelIds = getChannelIdsFromDB()
    for channelId in channelIds:
        generateEmbeddingsForChannel(channelId)


def getChannelIdsFromDB():
    return ["C01J8LJQ9Q9", "C01J8LJQ9Q9"]

async def generateEmbeddingsForChannel(channelId, chunked_content_path: str):
    credentials = load_credentials()
    token_provider = TokenProvider(credentials, stage=True)
    version = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    collection_name = f'mybuddy_product-help_{version}'
    emerald_client = EmeraldClient(token_provider, is_stage=True)
    collection_response = await emerald_client.create_collection(collection_name)

    with open(chunked_content_path, 'r') as f:
        chunked_content = json.load(f)
    
    batch_size = 100
    for start in range(0, len(chunked_content), batch_size):
        batch = chunked_content[start: start + batch_size]
        assets = []
        for item in batch:
            try:
                asset = await create_asset_from_entry(item)
                assets.append(asset)
            except Exception as e:
                print(f'Error creating asset for {item}')
                print(e)
        response = await emerald_client.add_assets(collection_name, assets)
        print(f'Added assets {start+len(batch)} out of {len(chunked_content)}')
        print(response)
    print(f'Assets uploaded at collection named {collection_name}')
    return

async def create_asset_from_entry(item):
    url = item.get('url')
    chunk_id = item.get('index')
    metadata = {
        'title': item.get('title', ''),
        'topics': item.get('topics', []),
        'headings': item.get('headings', []),
        'url': item.get('url', '')
    }
    # base64 encode url and chunk_id
    asset_id = base64.b64encode(f'{url}#{chunk_id}'.encode('utf-8')).decode('utf-8')
    data = item.get('text')
    asset = Asset(data, metadata, asset_id)
    return asset
