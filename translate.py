from googletrans import Translator
import nltk
import spacy

nlp = spacy.load('en_core_web_lg')
translator = Translator()
stemmer = nltk.stem.PorterStemmer()


def translate_text(user_message_text: str) -> str:
    languages = get_language_names_from_text(user_message_text)
    text = get_text_to_translate(user_message_text)

    if len(languages) == 0:  # Translate from automatically detected language to english
        translation = translator.translate(text)
    elif len(languages) == 1:
        detected_language = translator.detect(text)
        # The user has stated the language of the text
        if languages[0][:2] == detected_language or languages[0] == 'english':
            translation = translator.translate(text)
        else:
            translation = translator.translate(text, dest=languages[0][:2])
    else:
        translation = translator.translate(text, src=languages[0][:2], dest=languages[1][:2])

    return translation.text


def get_text_to_translate(text) -> str:
    languages = get_language_names_from_text(text)

    text = text.split()
    words_not_to_translate = set()

    tokens = nltk.word_tokenize(' '.join(text))
    tagged_words = nltk.pos_tag(tokens)
    for i in range(len(tagged_words) - 1):
        if ((tagged_words[i][1] == 'IN' or tagged_words[i][1] == 'TO')
                and tagged_words[i + 1][0] in languages) or tagged_words[i][0] in languages:
            words_not_to_translate.add(tagged_words[i][0])
            words_not_to_translate.add(tagged_words[i + 1][0])

    for word in text:
        if stemmer.stem(word) == "translat":
            words_not_to_translate.add(word)

    words_to_translate = [word for word in text if word not in words_not_to_translate]
    return ' '.join(words_to_translate)


def get_language_names_from_text(text) -> list:
    doc = nlp(text)

    languages = list()

    for entity in doc.ents:
        if entity.label_ == 'NORP' or entity.label_ == 'LANGUAGE':
            languages.append(entity.text)

    return languages
