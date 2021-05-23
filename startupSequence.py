import asyncio
import time
from lightscontroller import LED_COUNT

class StartupSequenceController:
    def __init__(self, config, servoController, lightsController, tts):
        audioConfig = config["AUDIO"]
        servoConfig = config["SERVO"]
        self.greeting = audioConfig["Greeting"]
        self.neutral = int(servoConfig["Neutral"])
        self.min = int(servoConfig["Min"])
        self.max = int(servoConfig["Max"])
        self.servoController = servoController
        self.lightsController = lightsController
        self.tts = tts
        self.startLoop()


    def startLoop(self):
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.doSequence())

    async def doSequence(self):
        self.lightsController.lightsOff()
        await asyncio.sleep(2)
        servoInterval = 0.25
        self.servoController.changeServo(self.neutral)
        await asyncio.sleep(servoInterval)
        self.servoController.changeServo(self.min)
        await asyncio.sleep(servoInterval)
        self.servoController.changeServo(self.max)
        await asyncio.sleep(servoInterval)
        
        transitionTime = float(1)
        startTime = time.time()
        targetTime = startTime + transitionTime
        servoTravel = self.max - self.neutral
        ledFraction = float(1) / LED_COUNT
        self.lightsController.lights.set_global_brightness(1)
        self.lightsController.lights.clear_strip()
        
        while time.time() < targetTime:
            timeFraction = (time.time() - startTime) / transitionTime
            servoPosition = self.max - servoTravel * timeFraction
            self.servoController.changeServo(servoPosition)
            ledsOn = round(timeFraction / ledFraction)
            for ix in range(0, ledsOn):
                self.lightsController.lights.set_pixel_rgb(LED_COUNT - ix - 1, 0x002e00)
            self.lightsController.lights.show()
            await asyncio.sleep(0.05)


        for ix in range(0, LED_COUNT):
            self.lightsController.lights.set_pixel_rgb(ix, 0x002e00)
        self.lightsController.lights.show()
        self.servoController.changeServo(self.neutral)

        if self.greeting:
            self.tts.sayText(self.greeting)

        await asyncio.sleep(0.1)
        self.lightsController.lightsOff()
        await asyncio.sleep(0.1)
        for ix in range(0, LED_COUNT):
            self.lightsController.lights.set_pixel_rgb(ix, 0x002e00)
        self.lightsController.lights.show()
        await asyncio.sleep(0.1)

        self.servoController.stopServo()
        self.lightsController.lights.set_global_brightness(31)
        self.lightsController.lights.clear_strip()
        