
from app.retriever.emerald_retriever import EmeraldRetriever
from app.clients.emerald import EmeraldClient, Asset
from app.ims.ims import load_credentials
from app.ims.ims import TokenProvider
from app.prompts.context_help import ContextualHelpPrompt
from app.genai.firefall_request import FireFallRequest
import os, asyncio
from dotenv import load_dotenv
load_dotenv()

TOP_N = os.environ.get('TOP_N_ELEMENTS')
THRESHOLD = os.environ.get('SIMILARITY_THRESHOLD')

def answer_question(item):
    return asyncio.run(answerQuestion(item))

async def answerQuestion(item):
    """Answer a question given a context."""
    query = item.get('text')
    channelId = item.get('channel')
    collection_name = f'mybuddy_embeddings_{channelId}'
    credentials = load_credentials()
    token_provider = TokenProvider(credentials, stage=True)
    emerald_client = EmeraldClient(token_provider, is_stage=True)
    retriever = EmeraldRetriever(emerald_client, collection_name)

    # Retrieve the top 5 answers
    slack_messages = await retriever.retrieve_async(query=query, top_n=TOP_N, threshold=THRESHOLD)
    documentations = [str(msg) for msg in slack_messages]
    contextual_help_prompt = ContextualHelpPrompt()

    resolved_prompt = contextual_help_prompt.resolve({"query": query, "documentations": documentations})

    firefall_request = (
            FireFallRequest.builder()
            .set_env(stage=True)
            .set_model('gpt-4')
            .set_max_tokens(3000)
            .set_temperature(0.0)
            .set_token_provider(token_provider)
            .build()
        )
    
    openai_response = await firefall_request.completions_async(resolved_prompt['dialogue']['question'])
    text = openai_response.response
    print('response of openAI is ', str(text))

    return text

def list_assets(item):
    asyncio.run(listAssets(item))
    return

async def listAssets(item):
    channelId = item.get('channelId')
    credentials = load_credentials()
    token_provider = TokenProvider(credentials, stage=True)
    emerald_client = EmeraldClient(token_provider, is_stage=True)
    collection_name = f'mybuddy_embeddings_{channelId}'
    assets = await emerald_client.list_assets(collection_name)
    print(assets)
    return assets


def get_asset(item):
    asyncio.run(getAsset(item))
    return

async def getAsset(item):
    channelId = item.get('channelId')
    credentials = load_credentials()
    token_provider = TokenProvider(credentials, stage=True)
    emerald_client = EmeraldClient(token_provider, is_stage=True)
    collection_name = f'mybuddy_embeddings_{channelId}'
    try:
        asset = await emerald_client.get_asset(collection_name, item.get('assetId',"test"))
    except Exception as e:
        if('Not Found' in str(e) ):
            print("Asset not found5")
        asset = "Asset not found"
    print(asset)
    return asset

def delete_collection(collection_name: str): 
    asyncio.run(deleteCollection(collection_name))
    return


async def deleteCollection(collection_name: str):
    credentials = load_credentials()
    token_provider = TokenProvider(credentials, stage=True)
    emerald_client = EmeraldClient(token_provider, is_stage=True)

    try:
        await emerald_client.delete_collection(collection_name)
    except Exception as e:
        print("Error in delete Collection " + str(e))

    return "Collection Deleted"

