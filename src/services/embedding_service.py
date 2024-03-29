import base64, re
from app.ims.ims import load_credentials
from app.ims.ims import TokenProvider
from app.clients.emerald import EmeraldClient, Asset
import asyncio
from parsers.wiki_loader import WikiLoader
from parsers.jira_loader import JiraLoader

wiki_url_regex = r'https?://wiki\.corp\.mycompany\.com/[^\s<>"]+'
jira_url_regex = r'https?://jira\.corp\.mycompany\.com/browse/[^\s<>"]+'

def generate_embeddings(item):
    asyncio.run(generateEmbeddings(item))
    return

async def generateEmbeddings(item):
    channelId = item.get('channel')
    credentials = load_credentials()
    token_provider = TokenProvider(credentials, stage=True)
    collection_name = f'mybuddy_embeddings_{channelId}'
    emerald_client = EmeraldClient(token_provider, is_stage=True)
    collection_list = await emerald_client.list_collections()  
    if collection_name not in collection_list:
        collection_response = await emerald_client.create_collection(collection_name)
        print(collection_response)
    else:
        print("collection already exists")
    
    # create assest and add to collection    
    asset_id = slack_msg_asset_id(item.get('thread_ts'))
    print('asset id is  neeraj '+  asset_id + "  thread_ts is " + item.get('thread_ts') )
    asset_msg = ''
    try:
        asset = await emerald_client.get_asset(collection_name, asset_id)
        if(asset is not None):
          asset_msg = asset["data"]
          print('asset found is ', asset_msg)
    except Exception as e:
        print('Asset not found ' , str(e))
  
    # check if wiki text include wiki link 
    # if yes, then extract the link and extract the content from wiki link and add to asset_msg
    if 'wiki.corp.mycompany.com' in item.get('text'):
        # get the wiki link from text
        print('text is ', item.get('text'))
        extracted_wiki_urls = re.findall(wiki_url_regex, item.get('text'))
        wiki_loader = WikiLoader()
        for wiki_link in extracted_wiki_urls:
            print('wiki link is ', wiki_link)
            wiki_content = wiki_loader.load_content(wiki_link)
            item['text'] = item['text'] + "\n Related Wiki html content is \n " + str(wiki_content)

    # check if slack text include jira link 
    if 'jira.corp.mycompany.com' in item.get('text'):
        extracted_jira_urls = re.findall(jira_url_regex, item.get('text'))
        jira_loader = JiraLoader()
        for jira_link in extracted_jira_urls:
            print('jira link is ', jira_link)
            jira_id = jira_loader.get_jira_issue_id_from_url(jira_link)
            json_response = jira_loader.get_jira_json(jira_id)
            jira_description = jira_loader.load_jira_desc(json_response)
            jira_comment = jira_loader.load_jira_comments(json_response)
            item['text'] = item['text'] + "\n Jira JSON content is \n " + str(jira_description)
            item['text'] = item['text'] + "\n" + str(jira_comment)
        
    item['text'] =  asset_msg + "\n" +  item.get('text',"")
    assets = []
    asset = create_asset_from_slack_message(item)
    assets.append(asset)
    await emerald_client.add_assets(collection_name, assets)
    print(f'Assets uploaded at collection named {collection_name}')
    return

def create_asset_from_slack_message(item):
    messageId = item.get('thread_ts')
    metadata = {
        'thread_id': item.get('thread_ts', []),
        'channel_id': item.get('channel', [])
    }
    # base64 encode url and chunk_id
    asset_id = slack_msg_asset_id(messageId)
    data = item.get('text')
    asset = Asset(data, metadata, asset_id)
    return asset

def create_asset_from_wiki_link(item):
    messageId = item.get('thread_ts')
    metadata = {
        'thread_id': item.get('thread_ts', []),
        'channel_id': item.get('channel', [])
    }
    # base64 encode url and chunk_id
    asset_id = slack_msg_asset_id(messageId)
    data = item.get('text')
    asset = Asset(data, metadata, asset_id)
    return asset


def slack_msg_asset_id(messageId):
    asset_id = base64.b64encode(f'message_{messageId}'.encode('utf-8')).decode('utf-8')
    return asset_id
  
