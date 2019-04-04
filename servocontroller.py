import asyncio
import time


class ServoController:

    def __init__(self, pi, config):
        servoConfig = config["SERVO"]
        self.pwmPin = int(servoConfig["PWMPin"])
        self.neutral = 75000
        self.amplitude = 25000
        self.frequency = 50
        self.changeVelocityPerSec = 25000
        self.shuttingDown = False
        # 1 is forward, -1 is backward, 0 is stop
        self.direction = 0
        self.timingLock = asyncio.Condition()
        self.pi = pi

    def forward(self):
        self.direction = 1

    def backward(self):
        self.direction = -1

    def lookStop(self):
        self.direction = 0

    def stop(self):
        with self.timingLock:
            print("Waiting for servo to stop...")
            self.shuttingDown = True
            self.timingLock.notify()

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.timingLoop())

    async def timingLoop(self):
        print("Servo starting...")
        initialSleep = 0.25
        # go neutral first
        self.pi.hardware_PWM(self.pwmPin, self.frequency, self.neutral)
        await asyncio.sleep(initialSleep)
        self.pi.hardware_PWM(self.pwmPin, self.frequency, self.neutral + int(self.amplitude / 2))
        await asyncio.sleep(initialSleep)
        self.pi.hardware_PWM(self.pwmPin, self.frequency, self.neutral - int(self.amplitude / 2))
        await asyncio.sleep(initialSleep)
        self.pi.hardware_PWM(self.pwmPin, self.frequency, self.neutral)
        await asyncio.sleep(initialSleep)
        self.pi.hardware_PWM(self.pwmPin, self.frequency, 0)

        currentPosition = self.neutral
        lastChangeTime = -1

        while True:
            async with self.timingLock:
                if not self.__shouldBeMoving(currentPosition):
                    self.pi.hardware_PWM(self.pwmPin, self.frequency, 0)
                    await self.timingLock.wait()

                if self.shuttingDown:
                    break

                if lastChangeTime == -1:
                    changeDelta = 0
                else:
                    timeDelta = time.time() - lastChangeTime
                    changeDelta = self.changeVelocityPerSec * timeDelta

                if self.direction == 1:
                    currentPosition = int(min(currentPosition + changeDelta, self.neutral + self.amplitude))
                elif self.direction == -1:
                    currentPosition = int(max(currentPosition - changeDelta, self.neutral - self.amplitude))

            self.pi.hardware_PWM(self.pwmPin, self.frequency, currentPosition)
            await asyncio.sleep(0)

        print("Servo stopping...")
        self.pi.hardware_PWM(self.pwmPin, self.frequency, 0)

    def __shouldBeMoving(self, currentPosition):
        if self.direction == 0:
            return False
        elif self.direction == 1 and currentPosition >= self.neutral + self.amplitude:
            return False
        elif self.direction == -1 and currentPosition <= self.neutral - self.amplitude:
            return False

        return True
