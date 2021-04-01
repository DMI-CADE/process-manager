class dmicEvent:

    def __init__(self):
        self._subs = []

    def __iadd__(self, sub):
        self._subs.append(sub)
        return self

    def update(self, event_args=None):
        for sub in self._subs:
            sub(event_args)
