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


def search(query: str):
    params = {
        "engine": "yandex",
        'yandex_domain': 'yandex.ru',
        "text": query,
        "api_key": SEARCH_API_KEY
    }
    search_ = GoogleSearch(params)
    results = search_.get_dict()
    organic_results = results['organic_results']

    for result in organic_results:
        link = result['link']
        if re.findall(r'music', link):
            assistant.link_to_search = link
            return query

    for result in organic_results:
        link = result['link']
        if re.findall(r'en\.wikipedia', link):
            assistant.link_to_search = link
            topic = link.split('/')[-1]
            return search_wikipedia(topic)

    assistant.link_to_search = results['search_metadata']['yandex_url']
    return query


def search_wikipedia(topic: str) -> str:
    page = wiki_wiki.page(topic)
    text = page.text
    sentences = text.split('.')
    return '.'.join(sentences[:5])


def search_youtube(user_message_text: str):
    query = ' '.join([word for word in user_message_text.split()
                      if "video" not in word and "youtube" not in word])
    if query:
        assistant.link_to_search = f'https://youtube.com/results?search_query={query}'
    else:
        assistant.link_to_search = f'https://youtube.com'
