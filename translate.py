from googletrans import Translator, LANGCODES
import nltk
from global_variables import nlp


translator = Translator()
stemmer = nltk.stem.PorterStemmer()


def translate_text(user_message_text: str) -> str:
    languages = get_language_names_from_text(user_message_text)
    text = get_text_to_translate(user_message_text)

    if len(languages) == 0:  # Translate from automatically detected language to english
        translation = translator.translate(text)
    elif len(languages) == 1:
        detected_language = translator.detect(text)
        # If the user has stated the language of the text
        if languages[0] == detected_language or languages[0] == 'english':
            translation = translator.translate(text)
        else:
            translation = translator.translate(text, dest=languages[0])
    else:
        translation = translator.translate(text, src=languages[0], dest=languages[0])

    return translation.text


def get_text_to_translate(text) -> str:
    languages = get_language_names_from_text(text)

    text = text.split()

    # Add language names (with prepositions before them) to words_not_to_translate
    tokens = nltk.word_tokenize(' '.join(text))  # Split the text into words
    tagged_words = nltk.pos_tag(tokens)  # Get a tag to each word in the text
    for i in range(len(tagged_words)):
        if i < len(tagged_words) - 1 \
                and ((tagged_words[i][1] == 'IN' or tagged_words[i][1] == 'TO')
                     and tagged_words[i + 1][0] in languages):
            tagged_words[i][0] = ""
            tagged_words[i + 1][0] = ""
        elif tagged_words[i][0] in languages or stemmer.stem(tagged_words[i][0] == "translat"):
            tagged_words[i][0] = ""

    words_to_translate = [word[0] for word in tagged_words if word[0]]
    return ' '.join(words_to_translate)  # Return the text without words_not_to_translate


def get_language_names_from_text(text) -> list:
    doc = nlp(text)

    languages = list()

    for entity in doc.ents:
        if entity.label_ == 'NORP' or entity.label_ == 'LANGUAGE':
            languages.append(entity.text)

    return languages
