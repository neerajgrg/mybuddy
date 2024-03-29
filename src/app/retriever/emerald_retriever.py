from app.clients.emerald import EmeraldClient
from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class SlackMessageChunk:
    text: str
    time_stamp: str
    thread_id: str
    channel_id: str

def emerald_to_chunk(emerald_data: dict) -> SlackMessageChunk:
    text = emerald_data.get('data')
    metadata = emerald_data.get('metadata')
    thread_id = 'p' + metadata.get('thread_id').replace('.', '')
    channel_id = metadata.get('channel_id')
    return {
        'text': text,
        'thread_id': thread_id,
        'channel_id': channel_id
    }
    # return SlackMessageChunk(text=text, time_stamp=time_stamp, thread_id=thread_id, channel_id=channel_id)

class EmeraldRetriever():
    """
    An Emerald embeddings based retriever that works on Chunks for MyBuddy Slack messages
    """
    def __init__(self, emerald_client: EmeraldClient, collection_name: str):
        """
        :param emerald_client: EmeraldClient instance
        :param collection_name: name of the collection to search in
        """
        super().__init__()
        self.emerald_client = emerald_client
        self.collection_name = collection_name

    async def retrieve_async(self, query: str, top_n: int = 5, threshold: float = 0.0) -> List[SlackMessageChunk]:
        """
        :param query: query string
        :param top_n: number of results to return
        :param threshold: threshold for the search
        """
        emerald_request = self.emerald_client.emerald_request()
        matched_assets_id = await emerald_request.search_asset(query,
                                                               self.collection_name, top_n, threshold=threshold)
        matched_assets = await emerald_request.get_asset_by_id(matched_assets_id,
                                                               self.collection_name)
        return [emerald_to_chunk(asset) for asset in matched_assets]

    def retrieve_sync(self, *args, **kwargs):
        raise NotImplementedError()