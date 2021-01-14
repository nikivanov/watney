import asyncio
import time
from events import Events

class StartupSequenceController:
    def __init__(self, config, servoController, lightsController, tts):
        Events.getInstance().janusFirstConnect.append(lambda: self.onJanusConnected())
        audioConfig = config["AUDIO"]
        servoConfig = config["SERVO"]
        self.greeting = audioConfig["Greeting"]
        self.neutral = int(servoConfig["Neutral"])
        self.min = int(servoConfig["Min"])
        self.max = int(servoConfig["Max"])
        self.servoController = servoController
        self.lightsController = lightsController
        self.tts = tts


    def onJanusConnected(self):
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.doSequence())

    async def doSequence(self):
        await asyncio.sleep(1)
        servoInterval = 0.25
        self.servoController.changeServo(self.neutral)
        await asyncio.sleep(servoInterval)
        self.servoController.changeServo(self.min)
        await asyncio.sleep(servoInterval)
        self.servoController.changeServo(self.max)
        await asyncio.sleep(servoInterval)
        self.servoController.changeServo(self.neutral)
        await asyncio.sleep(servoInterval)
        self.servoController.stopServo()

        lightsInterval = 0.1
        self.lightsController.lightsOn()
        await asyncio.sleep(lightsInterval)
        self.lightsController.lightsOff()
        await asyncio.sleep(lightsInterval)

        self.lightsController.lightsOn()
        await asyncio.sleep(lightsInterval)
        self.lightsController.lightsOff()
        await asyncio.sleep(lightsInterval)

        if self.greeting:
            self.tts.sayText(self.greeting)
        