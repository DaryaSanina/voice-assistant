import re
import os
from dotenv import load_dotenv

from serpapi import GoogleSearch
import wikipediaapi

import assistant

path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(path):
    load_dotenv(path)
    SEARCH_API_KEY = os.environ.get('SEARCH_API_KEY')

wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)


def search(text: str):
    params = {
        "engine": "yandex",
        "text": text,
        "api_key": SEARCH_API_KEY
    }
    search_ = GoogleSearch(params)
    results = search_.get_dict()
    print(results)
    organic_results = results['organic_results']

    for result in organic_results:
        link = result['link']
        if re.findall('en.wikipedia', link):
            assistant.link_to_search = link
            topic = link.split('/')[-1]
            return search_wikipedia(topic)

    assistant.link_to_search = results['search_metadata']['yandex_url']
    return text


def search_wikipedia(topic: str) -> str:
    page = wiki_wiki.page(topic)
    text = page.text
    sentences = text.split('.')
    print('.'.join(sentences[:5]))
    return '.'.join(sentences[:5])
