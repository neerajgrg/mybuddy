import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

class JiraLoader:
    jira_id_regex = r'/browse\/([A-Z]+-[0-9]+)'
    # jira_description_reg = 
    # jira_comment_reg =

    def __init__(self):
        self.auth_token = os.getenv('JIRA_BASEAUTH')
        self.api_endpoint = os.getenv('JIRA_API_ENDPOINT')
        self.headers = {
            'Authorization': f'Basic {self.auth_token}'
        }


    def get_jira_json(self, issue_id):  
        auth = os.getenv('JIRA_BASEAUTH')
        headers = {
            'Authorization': f'Basic {self.auth_token}',
            'Accept': 'application/json'
        }
        url = f'{self.api_endpoint}/{issue_id}'

        response = requests.get(url, headers=headers)
        print(response)
      #  response = requests.get(url, auth=auth, headers=headers)

        if response.status_code == 200:
            print('Responded 200')
            response_json = response.json()
            return response_json

            if 'fields' in response_json and 'description' in response_json['fields']:
                description = response_json['fields']['description']
                print("Description of the issue:", description)
                if 'fields' in response_json and 'comment' in response_json['fields']:
                    comments = response_json['fields']['comment']['comments']

                return description
            else:
                print("Description not found in the response JSON.")
                return description
        else:
            print(f"Failed to fetch Jira issue {issue_id}. Status code: {response.status_code}")
            return None

    def get_jira_issue_id_from_url(self, jira_url):
    # Split the URL by '/' and get the last part which contains the issue ID
        parts = jira_url.split('/')
        issue_id = parts[-1] if parts[-1] else parts[-2]  # Handle possible trailing slash

        return issue_id

    def load_jira_desc(self, response_json):
        if 'fields' in response_json and 'description' in response_json['fields']:
                description = response_json['fields']['description']
                print("Description of the issue:", description)
                return description
        else:
                print("Description not found in the response JSON.")
                return description


    def load_jira_comments(self, response_json):
        if 'fields' in response_json and 'comment' in response_json['fields']:
                comments = response_json['fields']['comment']['comments']
                return comments
        else:
            print("Comment not found in the response JSON.")
            return comments