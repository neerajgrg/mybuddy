
import json
from typing import Dict

class ContextualHelpPrompt():
    initial_prompt = """
    Given the below knowledge base:
    ```
    {documentation_prompt}
    ```
    Based on the above knowledge base can you try to answer the following question: Please formulate an answer in the form of a Slack message, utilizing Slack's Block Kit JSON format.
    For Providing refrences to slack threads, please use the below format:
    Example Slack thread format (only use if such a link exists in the knowledge base):
    https://franklin-testing.slack.com/archives/<channel_id>/<thread_id>

    Question:
    ```
    {query}
    ```

    If you are not able to answer it based on the knowledge base, then please respond with the below string only:
    "Sorry, Couldn't find any information in the knowledge base."
    """

    def __init__(self, word_limit=2000):
        self.word_limit = word_limit

    def resolve(self, parameters: Dict) -> Dict:
        documentations = parameters.get('documentations')
        separator = "\n"
        joined_documentation = separator.join(documentations)
        query: str = parameters.get('query')

        resolved_prompt = self.initial_prompt.format(documentation_prompt=joined_documentation, query=query)

        print('resolved prompt is ' +  resolved_prompt)

        return {
            "dialogue": {
                "question": resolved_prompt
            }
        }