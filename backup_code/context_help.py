
import json
from typing import Dict

class ContextualHelpPrompt():
    initial_prompt = """
    Here's a collection of information from our knowledge base:
    ```
    {documentation_prompt}
    ```
    A question based on this knowledge base has been asked. Please provide an answer in the form of a Slack message using Slack's Block Kit JSON format. Include emojis where appropriate. If the answer is not found in the provided information, respond with a Slack formatted block message indicating that the answer is not available.
    If appropriate, you can also provide a link to the slack threads using thread_ts from metadata that contain the answer and also add Reference Slack threads.
    Example Slack thread is https://franklin-testing.slack.com/archives/channel/thread_ts
    Question:
    ```
    {query}
    ```
    Note: The response should be crafted in a way that it can be directly used as a payload for Slack's API to send a message in a channel.
    """

    def __init__(self, word_limit=2000):
        self.word_limit = word_limit

    def resolve(self, parameters: Dict) -> Dict:
        documentations = parameters.get('documentations')
        separator = "\n"
        joined_documentation = separator.join(documentations)
        query: str = parameters.get('query')

        resolved_prompt = self.initial_prompt.format(documentation_prompt=joined_documentation, query=query)

        return {
            "dialogue": {
                "question": resolved_prompt
            }
        }