from events import Events

class JanusEventHandler:
    def __init__(self):
        self.sessions = set()

    def handleEvent(self, eventObj):
        sessionId = eventObj['session_id']
        eventType = eventObj['event']['name']
        if eventType == 'created':
            doFire = len(self.sessions) == 0
            self.sessions.add(sessionId)
            print("New janus session {}".format(sessionId))
            if doFire:
                print("Firing Session Started event")
                Events.getInstance().fireSessionStarted()
        elif eventType in ['timeout', 'destroyed']:
            doFire = len(self.sessions) > 0
            if sessionId in self.sessions:
                print("Removed Janus session {}".format(sessionId))
                self.sessions.remove(sessionId)
            if len(self.sessions) == 0 and doFire:
                print("Firing Session Ended event")
                Events.getInstance().fireSessionEnded()
