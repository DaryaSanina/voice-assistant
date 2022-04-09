import spacy
import os

SERVER_ADDRESS_HOST = '0.0.0.0'
SERVER_ADDRESS_PORT = int(os.environ.get("PORT", 5000))

nlp = spacy.load('en_core_web_lg')
