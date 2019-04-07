from events import Events
import asyncio
from webrtcclient import WebRTCClient


class AV:
    def __init__(self, config):
        Events.getInstance().sessionStarted.append(lambda: self.onSessionStarted())
        Events.getInstance().sessionEnded.append(lambda: self.onSessionEnded())
        self.webrtcClient = WebRTCClient()
        self.task = None

    def onSessionStarted(self):
        self.task = asyncio.get_event_loop().create_task(self.webrtcClient.start())

    def onSessionEnded(self):
        asyncio.get_event_loop().run_until_complete(self.task)

    def sayTTS(self, text):
        if self.webrtcClient.espeak:
            self.webrtcClient.espeak.props.text = text
