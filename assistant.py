# Singleton
class AssistantMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Assistant(metaclass=AssistantMeta):
    def answer(self, message_text):
        # TODO
        return message_text
