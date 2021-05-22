import asyncio
import shlex
from events import Events


class TTSSpeaker:
    def __init__(self, config, alsa, audioManager):
        self.alsa = alsa
        self.audioManager = audioManager
        self.audioToken = "08843f08-92aa-49b0-840f-74c6b38092ff"
        audioConfig = config["AUDIO"]
        self.ttsCommand = audioConfig["TTSCommand"]
        self.workQueue = asyncio.Queue()
        Events.getInstance().janusFirstConnect.append(lambda: self.onJanusConnected())

    def onJanusConnected(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.queueLoop())

    async def queueLoop(self):
        print("Starting TTS...")
        try:
            while True:
                ttsText = await self.workQueue.get()
                if ttsText:
                    print("Saying '{}'".format(ttsText))
                    self.audioManager.lowerVolume(self.audioToken)
                    fullTTSCommand = self.ttsCommand.format(shlex.quote(ttsText))
                    process = await asyncio.create_subprocess_shell(fullTTSCommand, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                    await process.communicate()
                    self.audioManager.restoreVolume(self.audioToken)
        except asyncio.CancelledError:
            print("TTS stopped")

    def sayText(self, text):
        self.workQueue.put_nowait(text)