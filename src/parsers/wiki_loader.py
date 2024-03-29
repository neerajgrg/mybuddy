import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

class WikiLoader:
    title_regex1 = r'/display/~[^/]+/(.+)'
    title_regex2 = r'title=([^&]+)'
    title_regex3 = r'/([^/]+)$'
    pageid_regex1 = r'pageId=([^&]+)'

    def __init__(self):
        self.auth_token = os.getenv('WIKI_ACCESS_TOKEN')
        self.api_endpoint = os.getenv('WIKI_REST_API_ENDPOINT')
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}'
        }

    def get_page_title_from_url(self, url):
        match = re.search(self.title_regex1, url)
        page_title = match.group(1) if match else None

        if page_title is None:
            match = re.search(self.title_regex2, url)
            page_title = match.group(1) if match else None

        if page_title is None:
            match = re.search(self.title_regex3, url)
            page_title = match.group(1) if match else ""

        return page_title.replace('+', ' ')

    def get_content_id_from_title(self, title):
        response = requests.get(f'{self.api_endpoint}?title={title}', headers=self.headers)
        if response.json() and response.json().get('results'):
            content_id = response.json()['results'][0]['id']
            return content_id

        return ""

    def get_content_id_from_url_via_title(self, url):
        page_title = self.get_page_title_from_url(url)

        if page_title:
            return self.get_content_id_from_title(page_title)

        return ""

    def get_content_id_from_url_via_regex(self, url):
        match = re.search(self.pageid_regex1, url)
        content_id = match.group(1).replace('+', ' ') if match else ""
        return content_id

    def get_content_id(self, url):
        content_id = self.get_content_id_from_url_via_regex(url)
        if not content_id:
            content_id = self.get_content_id_from_url_via_title(url)
        return content_id

    def get_children(self, url):
        content_id = self.get_content_id(url)
        if content_id:
            response = requests.get(f'{self.api_endpoint}/{content_id}/child/page', headers=self.headers)
            if response.json() and response.json().get('results'):
                ids = [f"https://wiki.corp.mycompany.com{content['_links']['webui']}" for content in response.json()['results']]
                return ids

        return []

    def get_content_by_id(self, content_id):
        try:
            response = requests.get(f'{self.api_endpoint}/{content_id}?expand=body.view,title', headers=self.headers)
            content = response.json().get('body', {}).get('view', {}).get('value', '')
            title = response.json().get('title', '')

            return {'content': content, 'title': title}
        except Exception as e:
            print(f"Error retrieving content for content ID: {content_id}", e)

        return {'content': "", 'title': ""}

    def load_content(self, url):
        content_id = self.get_content_id(url)
        if content_id:
            content_data = self.get_content_by_id(content_id)
            if content_data['content']:
                text = content_data['content']

                return {'texts': text, 'name': content_data['title']}
        else:
            print('Page with the provided title not found.')

        return {'texts': "", 'name': url}

    def accepts(self, json):
        url = json.get('url', '')
        return os.getenv('WIKI_LOADER_ACCEPT_DOMAIN') in url

# Usage example
# wiki_loader = WikiLoader(json_data)
# content = wiki_loader.load_content(some_url)
