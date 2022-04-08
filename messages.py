class Message:
    def __init__(self, text, sender):
        self.text = text
        self.sender = sender

    def __repr__(self):
        return self.text
