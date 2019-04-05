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
        # 1 is forward, -1 is backward, 0 is stop
        self.direction = 0
        self.timingLock = asyncio.Condition()
        self.pi = pi
        self.task = None

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
            deltas = list()

            while True:
                async with self.timingLock:
                    if not self.__shouldBeMoving(currentPosition):
                        self.pi.hardware_PWM(self.pwmPin, self.frequency, 0)
                        lastChangeTime = -1
                        if len(deltas) > 0:
                            print("Average change: {}, total: {}".format(sum(deltas) / len(deltas), len(deltas)))
                        deltas.clear()
                        print("Servo sleeping")
                        await self.timingLock.wait()
                        print("Servo woke up")

                    if lastChangeTime == -1:
                        changeDelta = 0
                    else:
                        timeDelta = time.time() - lastChangeTime
                        changeDelta = self.changeVelocityPerSec * timeDelta

                    lastChangeTime = time.time()
                    deltas.append(changeDelta)

                    if self.direction == 1:
                        currentPosition = int(min(currentPosition + changeDelta, self.neutral + self.amplitude))
                    elif self.direction == -1:
                        currentPosition = int(max(currentPosition - changeDelta, self.neutral - self.amplitude))

                self.pi.hardware_PWM(self.pwmPin, self.frequency, currentPosition)
                await asyncio.sleep(0)
        except asyncio.CancelledError:
            print("Servo stopping...")
            self.pi.hardware_PWM(self.pwmPin, self.frequency, 0)
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
