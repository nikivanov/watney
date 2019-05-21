import asyncio
import shlex
from events import Events


class TTSSpeaker:
    def __init__(self, config, alsa):
        self.alsa = alsa
        audioConfig = config["AUDIO"]
        self.ttsCommand = audioConfig["TTSCommand"]
        self.greeting = audioConfig["Greeting"]
        self.workQueue = asyncio.Queue()
        Events.getInstance().janusFirstConnect.append(lambda: self.onJanusConnected())

    def onJanusConnected(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.queueLoop())
        if self.greeting:
            self.workQueue.put_nowait(self.greeting)

    async def queueLoop(self):
        print("Starting TTS...")
        await asyncio.sleep(2)  # let the servo spin
        try:
            while True:
                ttsText = await self.workQueue.get()
                if ttsText:
                    print("Saying '{}'".format(ttsText))
                    fullTTSCommand = self.ttsCommand.format(shlex.quote(ttsText))
                    mute = False
                    if self.alsa.isMuted:
                        self.alsa.unmute()
                        mute = True
                    process = await asyncio.create_subprocess_shell(fullTTSCommand, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                    await process.communicate()
                    if mute:
                        self.alsa.mute()
        except asyncio.CancelledError:
            print("TTS stopped")

    def sayText(self, text):
        self.workQueue.put_nowait(text)