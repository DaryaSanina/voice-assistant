import spacy

SERVER_ADDRESS_HOST = '127.0.0.1'
SERVER_ADDRESS_PORT = 8000

try:
    nlp = spacy.load("en_core_web_md")
except:
    spacy.cli.download("en_core_web_md")
    nlp = spacy.load("en_core_web_md")
