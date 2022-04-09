import weather
from global_variables import nlp

import datetime
import nltk

stemmer = nltk.stem.PorterStemmer()

events = list()


class Event:
    def __init__(self, name, date=datetime.date.today(), time=None, place=None):
        self.name = name
        self.date = date
        self.time = time
        self.place = place

        self.notification_24_hours = False
        self.notification_2_hours = False
        self.notification_10_minutes = False


def get_time_from_text(text) -> (datetime.time, str):
    doc = nlp(text)

    for entity in doc.ents:
        if entity.label_ == "TIME":
            time = entity.text.split()
            if len(time) == 3:
                if time[2] == 'PM':
                    time = datetime.time(hour=int(entity.text.split(' ')[0]) + 12,
                                         minute=int(entity.text.split(' ')[1]))
                    return time, entity.text
                else:
                    time = datetime.time(hour=int(entity.text.split(' ')[0]),
                                         minute=int(entity.text.split(' ')[1]))
                    return time, entity.text
            elif time[1] == 'AM':
                time = datetime.time(hour=int(entity.text.split(' ')[0]))
                return time, entity.text
            elif time[1] == 'PM':
                time = datetime.time(hour=int(entity.text.split(' ')[0]) + 12)
                return time, entity.text
    return None, ''


def add_event(text):
    place = weather.get_geopolitical_entity_from_text(text)
    delta_days, date_str = weather.get_delta_days_from_text(text)
    time, time_str = get_time_from_text(text)

    tokens = nltk.word_tokenize(text)  # Split the text into words
    tagged_words = nltk.pos_tag(tokens)  # Get a tag to each word in the text
    text = text

    if text.find("plan") != -1:
        word_start = text.find("plan")
        word_end = word_start + 4
        text = text[:word_start] + text[word_end + 1:]
        tokens = nltk.word_tokenize(text)
        tagged_words = nltk.pos_tag(tokens)

    if text.find("event") != -1:
        word_start = text.find("event")
        word_end = word_start + 5
        prev_word_end = word_start - 1
        prev_word_start = prev_word_end
        while prev_word_start > 0 and text[prev_word_start - 1] != ' ':
            prev_word_start -= 1

        if prev_word_start != prev_word_end \
                and tagged_words[text.split().index(text[prev_word_start:prev_word_end])][1] == 'DT':
            text = text[:word_start] + text[prev_word_end + 1:]
            tokens = nltk.word_tokenize(text)
            tagged_words = nltk.pos_tag(tokens)
        else:
            text = text[:word_start] + text[word_end + 1:]
            tokens = nltk.word_tokenize(text)
            tagged_words = nltk.pos_tag(tokens)

    if place:
        word_start = text.find(place)
        word_end = word_start + len(place)
        prev_word_end = word_start - 1
        prev_word_start = prev_word_end
        while prev_word_start > 0 and text[prev_word_start - 1] != ' ':
            prev_word_start -= 1

        if prev_word_start != prev_word_end \
                and tagged_words[text.split().index(text[prev_word_start:prev_word_end])][1] == 'IN':
            text = text[:prev_word_start] + text[word_end + 1:]
            tokens = nltk.word_tokenize(text)
            tagged_words = nltk.pos_tag(tokens)
        else:
            text = text[:word_start] + text[word_end + 1:]
            tokens = nltk.word_tokenize(text)
            tagged_words = nltk.pos_tag(tokens)

    if date_str:
        word_start = text.find(date_str)
        word_end = word_start + len(date_str)
        prev_word_end = word_start - 1
        prev_word_start = prev_word_end - 1
        while prev_word_start > 0 and text[prev_word_start - 1] != ' ':
            prev_word_start -= 1

        if prev_word_start != prev_word_end \
                and tagged_words[text.split().index(text[prev_word_start:prev_word_end])][1] == 'IN':
            text = text[:prev_word_start] + text[word_end + 1:]
            tokens = nltk.word_tokenize(text)
            tagged_words = nltk.pos_tag(tokens)
        else:
            text = text[:word_start] + text[word_end + 1:]
            tokens = nltk.word_tokenize(text)
            tagged_words = nltk.pos_tag(tokens)

    if time_str:
        if text.find(time_str) != -1:
            word_start = text.find(time_str)
            word_end = word_start + len(time_str)
            prev_word_end = word_start - 1
            prev_word_start = prev_word_end - 1
            while prev_word_start > 0 and text[prev_word_start - 1] != ' ':
                prev_word_start -= 1

            if prev_word_start != prev_word_end \
                    and tagged_words[text.split().index(text[prev_word_start:prev_word_end])][1] == 'IN':
                text = text[:prev_word_start] + text[word_end + 1:]
            else:
                text = text[:word_start] + text[word_end + 1:]

    event = Event(name=text.strip(),
                  date=datetime.date.today() + datetime.timedelta(days=delta_days),
                  time=time, place=place)
    events.append(event)
