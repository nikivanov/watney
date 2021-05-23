instance = None


class Events:
    sessionStarted = list()
    sessionEnded = list()

    @staticmethod
    def getInstance():
        global instance
        if instance is None:
            instance = Events()

        return instance

    def fireSessionStarted(self):
        for eventFn in self.sessionStarted:
            try:
                eventFn()
            except Exception as e:
                print("Exception on sessionStarted: {}".format(e))

    def fireSessionEnded(self):
        for eventFn in self.sessionEnded:
            try:
                eventFn()
            except Exception as e:
                print("Exception on sessionEnded: {}".format(e))

