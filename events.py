instance = None


class Events:
    sessionStarted = list()
    sessionEnded = list()

    onCharger = list()
    offCharger = list()

    motionOn = list()
    motionOff = list()

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
                print("Exception in sessionStarted: {}".format(e))

    def fireSessionEnded(self):
        for eventFn in self.sessionEnded:
            try:
                eventFn()
            except Exception as e:
                print("Exception in sessionEnded: {}".format(e))

    def fireOnCharger(self):
        for eventFn in self.onCharger:
            try:
                eventFn()
            except Exception as e:
                print("Exception in onCharger: {}".format(e))

    def fireOffCharger(self):
        for eventFn in self.offCharger:
            try:
                eventFn()
            except Exception as e:
                print("Exception in offCharger: {}".format(e))

    def fireMotionOn(self):
        for eventFn in self.motionOn:
            try:
                eventFn()
            except Exception as e:
                print("Exception in motionOn: {}".format(e))

    def fireMotionOff(self):
        for eventFn in self.motionOff:
            try:
                eventFn()
            except Exception as e:
                print("Exception in motionOff: {}".format(e))


    

