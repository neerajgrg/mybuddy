from flask import Blueprint, request, jsonify, make_response
from app.clients.slack import SlackClient
import os, json
from dotenv import load_dotenv
from services.embedding_service import generate_embeddings
from services.query_service import answer_question
from functools import lru_cache
from templates.slack_responses import simple_greeting_template

# Load environment variables
load_dotenv()
# Initialize Slack Client with environment variables
slack_client = SlackClient(os.environ['SLACK_BOT_TOKEN'], os.environ['SLACK_SIGNING_SECRET'])
slack_bot_id = os.environ['SLACK_BOT_ID']

# Create a Flask blueprint
slack_bp = Blueprint('slack_bp', __name__)
processed_events = set()

@slack_bp.route('/events', methods=['POST'])
def slack_events():
    if not slack_client.is_valid_request(request):
        return make_response("Invalid request", 403)
    try:
        event_data = request.json
        if 'challenge' in event_data:
             return make_response(event_data['challenge'], 200)
        handle_event(event_data)
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return make_response("Error processing event", 500)
    return make_response("OK", 200)


@lru_cache(maxsize=1024)
def is_event_processed(event_id):
    if 'processed_events' not in is_event_processed.__dict__:
        is_event_processed.processed_events = set()

    if event_id in is_event_processed.processed_events:
        return True

    is_event_processed.processed_events.add(event_id)
    return False

def handle_event(event_data):
    if event_data['type'] == 'event_callback':
        process_event_callback(event_data['event'])
    return

def process_event_callback(event):
    text = event['text']
    channel_info = slack_client.get_channel_info(channel_id=event.get('channel'))
    channel_description = channel_info['channel']['purpose']['value']
    channel_config = parse_config(channel_description)
    if 'bot_id' not in event and f'<@{slack_bot_id}>' in text and 'subtype' not in event:
        respond_to_app_mention(event, channel_config)
        return
    elif event['type'] == 'message' and 'bot_id' not in event and 'learning_mode' in channel_config and channel_config['learning_mode'] == 'on':
        resposne = slack_client.add_reaction_to_message(event['channel'], event['event_ts'], 'bookmark')
        if not resposne:
            print("Reaction already added")
            return
       
        item = {}
        item['text'] = event.get('text',"")
        item['channel'] = event.get('channel',"")
        if 'thread_ts' in event:
            item['thread_ts'] = event['thread_ts']
        else:
            item['thread_ts'] = event['ts']
        item['event_ts'] = event.get('event_ts',"")
        generate_embeddings(item)
        return

def respond_to_app_mention(event , channel_config):
    text = event['text'].lower()
    channel = event['channel']
    thread_ts = event['ts']

    item = {}
    item['text'] = event.get('text',"").replace(f'<@{slack_bot_id}>', '').strip()
    item['channel'] = event.get('channel',"")
    item['thread_ts'] = thread_ts
    item['time_stamp'] = event.get('event_ts',"")

    if 'setup help' in text:
        slack_client.post_message_with_thread_ts(channel, simple_greeting_template, thread_ts)
    elif 'buddy ready?' in text:
        if is_channel_ready(channel, channel_config):
             slack_client.post_message_with_thread_ts(channel, "Slack bot is ready! 👍", thread_ts)
        else:
             slack_client.post_message_with_thread_ts(channel, "Slack bot is not ready. Please add Requirement config in channel description", thread_ts)
    else:
        response = slack_client.add_reaction_to_message(event['channel'], event['ts'], 'eyes')
        if not response:
            print("Reaction already added")
            return
        answer = answer_question(item)
        slack_client.post_message_with_thread_ts(channel, answer, thread_ts)


def is_channel_ready(channel_id, channel_config):
    required_keys = ["learning_mode", "jira_integration","wiki_integration"]  # Replace with actual keys
    return all(key in channel_config for key in required_keys)

def parse_config(description):
    config_dict = {}
    lines = description.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            config_dict[key.strip()] = value.strip()
    return config_dict
