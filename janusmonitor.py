from threading import Thread
import requests
import uuid
import time


class JanusMonitor:

    def __init__(self):
        self.hasOpenSession = False
        self.watchers = list()
        print("Starting the janus session monitor")
        self.workerThread = Thread(target=self.workLoop, daemon=True)
        self.workerThread.start()

    def workLoop(self):
        lastRequestFailed = True
        while True:
            try:
                self.handleSessionsObject(self.getSessions().json())
                lastRequestFailed = False
            except Exception as e:
                if not lastRequestFailed:
                    print("Janus session request failed: " + str(e))
                lastRequestFailed = True

            time.sleep(1)

    def handleSessionsObject(self, list_sessions):
        sessionPresent = len(list_sessions["sessions"]) > 0
        if sessionPresent != self.hasOpenSession:
            self.hasOpenSession = sessionPresent
            print("Session presence: " + str(self.hasOpenSession))
            for watcher in self.watchers:
                try:
                    watcher(self.hasOpenSession)
                except Exception as e:
                    print("Watcher threw an exception: " + str(e))

    def getSessions(self):
        return requests.post("http://localhost:7088/admin", json=
        {
            "janus": "list_sessions",
            "transaction": str(uuid.uuid4()),
            "admin_secret": "janusoverlord"
        })

    def addWatcher(self, watcherFunc):
        self.watchers.append(watcherFunc)


