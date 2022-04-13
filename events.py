import weather
from global_variables import nlp

import datetime
import nltk

from data import db_session
from data.event_models import EventModel

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


def load_events(current_user):
    global events

    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user_id = current_user.id

        database_events = db_sess.query(EventModel) \
            .filter(EventModel.user_id == user_id).all()
        events = list()
        for event in database_events:
            events.append(Event(name=event.name, date=event.date, time=event.time,
                                place=event.place))


def update_database(current_user):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()

        if not db_sess.query(EventModel).filter(EventModel.name == events[-1].name).first():
            user_id = current_user.id

            event = EventModel(user_id=user_id, name=events[-1].name, date=events[-1].date,
                               time=events[-1].time, place=events[-1].place)
            db_sess.add(event)

            db_sess.commit()


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
