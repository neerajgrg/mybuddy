from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
import json


def is_json(str):
    try:
        json_object = json.loads(str)
    except ValueError as e:
        return False
    return True

class SlackClient:
    def __init__(self, token, signing_secret):
        self.client = WebClient(token=token)
        self.signature_verifier = SignatureVerifier(signing_secret)

    def post_message_with_thread_ts(self, channel, message, thread_ts=None):
        response = {}
        if isinstance(message, dict):
            message = json.dumps(message)
        print
        try:
            if is_json(message):
                block_message = json.loads(message)
                response = self.client.chat_postMessage(
                    channel=channel,
                    blocks=block_message["blocks"],
                    thread_ts=thread_ts
                )
            else:
                response = self.client.chat_postMessage(
                    channel=channel,
                    text=message,
                    thread_ts=thread_ts
                )
            print(response)
        except SlackApiError as e:
            print(f"Error posting message: {e}")
            return False
        return True
    
    def post_message(self, channel, message):
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
            )
        except SlackApiError as e:
            print(f"Error posting message: {e}")
            return False
        return True

    def post_message_with_blocks(self, channel, message, blocks):
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                blocks=blocks
            )
        except SlackApiError as e:
            print(f"Error posting message: {e}")
            return False
        return True

    def post_message_with_attachments(self, channel, message, attachments):
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                attachments=attachments
            )
        except SlackApiError as e:
            print(f"Error posting message: {e}")
            return False
        return True

    def post_message_with_attachments_and_blocks(self, channel, message, attachments, blocks):
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                attachments=attachments,
                blocks=blocks
            )
        except SlackApiError as e:
            print(f"Error posting message: {e}")
            return False
        return True

    def post_message_with_attachments_blocks_and_thread_ts(self, channel, message, attachments, blocks, thread_ts):
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                attachments=attachments,
                blocks=blocks,
                thread_ts=thread_ts
            )
        except SlackApiError as e:
            print(f"Error posting message: {e}")
            return False
        return True

    def post_message_with_attachments_blocks_thread_ts_and_reply_broadcast(self, channel, message, attachments, blocks, thread_ts, reply_broadcast):
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                attachments=attachments,
                blocks=blocks,
                thread_ts=thread_ts,
                reply_broadcast=reply_broadcast
            )
        except SlackApiError as e:
            print(f"Error posting message: {e}")
            return False
        return True
    
    def is_valid_request(self, req):
        return self.signature_verifier.is_valid_request(req.get_data(), req.headers)
    
    def get_channel_info(self, channel_id):
        response = {}
        try:
            response = self.client.conversations_info(
                channel=channel_id
            )
        except SlackApiError as e:
            print(f"Error fetching channel info: {e}")
        return response
    

    def add_reaction_to_message(self, channel, event_ts, emoji):
        """
        Add an emoji reaction to a message in a Slack channel.
        
        :param channel: The ID of the channel containing the message.
        :param timestamp: The timestamp of the message to react to.
        :param emoji: The name of the emoji to add (e.g., 'thumbsup').
        """
        try:
            response = self.client.reactions_add(
                channel=channel,
                timestamp=event_ts,
                name=emoji
            )
        except SlackApiError as e:
            return False
        return True