import asyncio
import time
import RPi.GPIO as GPIO


class ServoController:

    def __init__(self, config):
        servoConfig = config["SERVO"]
        self.pwmPin = int(servoConfig["PWMPin"])
        self.neutral = 7.5
        self.amplitude = 2.5
        self.frequency = 50
        self.changeVelocityPerSec = 2.5
        # 1 is forward, -1 is backward, 0 is stop
        self.direction = 0
        self.timingLock = asyncio.Condition()
        self.task = None
        GPIO.setup(self.pwmPin, GPIO.OUT)
        self.pwmControl = GPIO.PWM(self.pwmPin, self.frequency)
        self.pwmControl.start(0)

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
            self.direction = 0
            self.timingLock.notify()

    def start(self):
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.timingLoop())

    def stop(self):
        if self.task:
            self.task.cancel()

    async def timingLoop(self):
        print("Servo starting...")

        try:
            initialSleep = 0.25
            # go neutral first
            self.pwmControl.ChangeDutyCycle(self.neutral)
            await asyncio.sleep(initialSleep)
            self.pwmControl.ChangeDutyCycle(self.neutral + self.amplitude / 2)
            await asyncio.sleep(initialSleep)
            self.pwmControl.ChangeDutyCycle(self.neutral - self.amplitude / 2)
            await asyncio.sleep(initialSleep)
            self.pwmControl.ChangeDutyCycle(self.neutral)
            await asyncio.sleep(initialSleep)
            self.pwmControl.ChangeDutyCycle(0)

            currentPosition = self.neutral
            lastChangeTime = None
            while True:
                async with self.timingLock:
                    if not self.__shouldBeMoving(currentPosition):
                        self.pwmControl.ChangeDutyCycle(0)
                        lastChangeTime = None
                        await self.timingLock.wait()

                if not lastChangeTime:
                    changeDelta = 0
                else:
                    timeDelta = time.time() - lastChangeTime
                    changeDelta = self.changeVelocityPerSec * timeDelta

                lastChangeTime = time.time()

                if self.direction == 1:
                    currentPosition = min(currentPosition + changeDelta, self.neutral + self.amplitude)
                elif self.direction == -1:
                    currentPosition = max(currentPosition - changeDelta, self.neutral - self.amplitude)

                self.pwmControl.ChangeDutyCycle(currentPosition)
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            self.pwmControl.ChangeDutyCycle(0)
            print("Servo stopped")
        except Exception as e:
            print("Unexpected exception in servo: " + str(e))

    def __shouldBeMoving(self, currentPosition):
        if self.direction == 0:
            return False
        elif self.direction == 1 and currentPosition >= self.neutral + self.amplitude:
            return False
        elif self.direction == -1 and currentPosition <= self.neutral - self.amplitude:
            return False

        return True
