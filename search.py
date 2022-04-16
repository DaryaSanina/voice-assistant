import re
import os
from dotenv import load_dotenv

from serpapi import GoogleSearch
import wikipediaapi

import assistant

# Get search API key
path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(path):
    load_dotenv(path)
    SEARCH_API_KEY = os.environ.get('SEARCH_API_KEY')

wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)

YANDEX_LANGCODES = {"russian": "ru", "english": "en", "belorussian": "be", "french": "fr",
                    "german": "de", "indonesian": "id", "kazakh": "kk", "tatar": "tt",
                    "turkish": "tr", "ukrainian": "uk"}


def search(query: str, language: str):
    # Make a request
    if language in YANDEX_LANGCODES.keys():  # If searching in the user's language is available
        params = {
            "engine": "yandex",
            'yandex_domain': 'yandex.ru',
            "text": query,
            "api_key": SEARCH_API_KEY,
            "lang": YANDEX_LANGCODES[language]
        }
    else:
        params = {
            "engine": "yandex",
            'yandex_domain': 'yandex.ru',
            "text": query,
            "api_key": SEARCH_API_KEY,
            "lang": "en"
        }

    search_ = GoogleSearch(params)
    results = search_.get_dict()
    organic_results = results['organic_results']  # Results of the search

    # Iterate through the results
    for result in organic_results:
        link = result['link']
        if re.findall(r'music\.yandex', link):  # If there is a Yandex.Music link in the results
            assistant.link_to_search = link
            return query

        if re.findall(r'wikipedia', link):  # If there is a Wikipedia link in the results
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
