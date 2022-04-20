import asyncio
import time
import uuid

class ServoController:

    def __init__(self, gpio, pwmPin, neutral, minimum, maximum, audioManager):
        self.pwmPin = pwmPin
        self.neutral = neutral
        self.min = minimum
        self.max = maximum

        self.audioManager = audioManager
        self.audioToken = uuid.uuid4()

        self.gpio = gpio

        self.changeVelocityPerSec = 1000
        # 1 is forward, -1 is backward, 0 is stop
        self.direction = 0
        self.timingLock = asyncio.Condition()
        self.task = None
        self.startLoop()

    async def forward(self):
        async with self.timingLock:
            self.direction = 1
            self.timingLock.notify()

    async def backward(self):
        async with self.timingLock:
            self.direction = -1
            self.timingLock.notify()

    async def lookStop(self):
        async with self.timingLock:
            if self.direction != 0:
                self.direction = 0
                self.timingLock.notify()

    def startLoop(self):
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.timingLoop())

    async def timingLoop(self):
        print("Servo starting...")
        try:
            currentPosition = self.neutral
            lastChangeTime = None
            while True:
                async with self.timingLock:
                    if not self.__shouldBeMoving(currentPosition):
                        self.stopServo()
                        self.audioManager.restoreVolume(self.audioToken)
                        lastChangeTime = None
                        await self.timingLock.wait()

                self.audioManager.lowerVolume(self.audioToken)
                if not lastChangeTime:
                    changeDelta = 0
                else:
                    timeDelta = time.time() - lastChangeTime
                    changeDelta = self.changeVelocityPerSec * timeDelta

                lastChangeTime = time.time()

                if self.direction == 1:
                    currentPosition = max(currentPosition - changeDelta, self.min)
                elif self.direction == -1:
                    currentPosition = min(currentPosition + changeDelta, self.max)

                self.changeServo(currentPosition)
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            self.stopServo()
            print("Servo stopped")
        except Exception as e:
            print("Unexpected exception in servo: " + str(e))

    def __shouldBeMoving(self, currentPosition):
        if self.direction == 0:
            return False
        elif self.direction == 1 and currentPosition <= self.min:
            return False
        elif self.direction == -1 and currentPosition >= self.max:
            return False

        return True

    def stopServo(self):
        self.gpio.set_servo_pulsewidth(self.pwmPin, 0)

    def changeServo(self, val):
        self.gpio.set_servo_pulsewidth(self.pwmPin, val)

    def stop(self):
        self.stopServo()