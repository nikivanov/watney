import pigpio
from threading import Thread, Condition
import time


class ServoController:

    def __init__(self, pi, pwmPin):
        self.pwmPin = pwmPin
        self.neutral = 75000
        self.amplitude = 25000
        self.frequency = 50
        self.speed_per_sec = 30000
        self.resolution = 0.03
        self.shuttingDown = False

        # 1 is forward, -1 is backward, 0 is stop
        self.direction = 0

        self.pi = pi

        self.timingLock = Condition()
        self.timingThread = Thread(daemon=True, target=self.timingLoop)
        self.timingThread.start()

    def forward(self):
        with self.timingLock:
            self.direction = 1
            self.timingLock.notify()

    def backward(self):
        with self.timingLock:
            self.direction = -1
            self.timingLock.notify()

    def lookStop(self):
        with self.timingLock:
            self.direction = 0
            self.timingLock.notify()

    def stop(self):
        with self.timingLock:
            print("Waiting for servo to stop...")
            self.shuttingDown = True
            self.timingLock.notify()

        print("Joining the timing thread")
        self.timingThread.join()
        print("Servo thread stopped")

    def timingLoop(self):
        print("Servo starting...")
        initialSleep = 0.25
        # go neutral first
        self.pi.hardware_PWM(self.pwmPin, self.frequency, self.neutral)
        time.sleep(initialSleep)
        self.pi.hardware_PWM(self.pwmPin, self.frequency, self.neutral + int(self.amplitude / 2))
        time.sleep(initialSleep)
        self.pi.hardware_PWM(self.pwmPin, self.frequency, self.neutral - int(self.amplitude / 2))
        time.sleep(initialSleep)
        self.pi.hardware_PWM(self.pwmPin, self.frequency, self.neutral)
        time.sleep(initialSleep)
        self.pi.hardware_PWM(self.pwmPin, self.frequency, 0)

        currentPosition = self.neutral
        lastChangeTime = -1

        while True:
            with self.timingLock:
                if not self.__shouldBeMoving(currentPosition):
                    self.pi.hardware_PWM(self.pwmPin, self.frequency, 0)
                    self.timingLock.wait()

                if self.shuttingDown:
                    break

                if lastChangeTime == -1:
                    changeDelta = self.speed_per_sec * self.resolution
                else:
                    timeDelta = time.time() - lastChangeTime
                    changeDelta = self.speed_per_sec * timeDelta

                if self.direction == 1:
                    currentPosition = int(min(currentPosition + changeDelta, self.neutral + self.amplitude))
                elif self.direction == -1:
                    currentPosition = int(max(currentPosition - changeDelta, self.neutral - self.amplitude))

            # print("Pin {} frequency {} position {}".format(self.pwmPin, self.frequency, currentPosition))
            self.pi.hardware_PWM(self.pwmPin, self.frequency, currentPosition)
            time.sleep(self.resolution)

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
