import configparser
import pigpio
from threading import Thread, Condition
import time
import os
import sys


class Motor:
    PWM_FREQUENCY = 200

    def __init__(self, pi, pwmPin, forwardPin, reversePin, trim):
        self.pi = pi
        self.pwmPin = pwmPin
        self.forwardPin = forwardPin
        self.reversePin = reversePin
        self.pwmControl = None
        self.trim = trim
        self.__initMotor()

    def __initMotor(self):
        self.pi.set_mode(self.forwardPin, pigpio.OUTPUT)
        self.pi.set_mode(self.reversePin, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(self.pwmPin, self.PWM_FREQUENCY)
        self.stop()

    def stop(self):
        self.pi.write(self.forwardPin, 0)
        self.pi.write(self.reversePin, 0)

    def setMotion(self, dutyCycle):
        self.stop()

        if dutyCycle != 0:
            if dutyCycle >= 0:
                self.pi.write(self.forwardPin, 1)
            else:
                self.pi.write(self.reversePin, 1)

            targetDC = abs(dutyCycle * self.trim)

            # below 20 DC, the motor will stall, which isn't good for anybody
            if targetDC > 20:
                self.pi.set_PWM_dutycycle(self.pwmPin, int(targetDC / 100 * 255))
            else:
                self.pi.set_PWM_dutycycle(self.pwmPin, 0)


class MotorController:
    validBearings = ["n", "ne", "e", "se", "s", "sw", "w", "nw", "0"]

    def __init__(self, leftMotor, rightMotor, halfTurnSpeed, softTurnForwardRatio, softTurnPeriod):
        self.leftMotor = leftMotor
        self.rightMotor = rightMotor
        self.halfTurnSpeed = halfTurnSpeed

        self.softTurnForwardSec = softTurnPeriod * softTurnForwardRatio
        self.softTurnBackwardsSec = softTurnPeriod * (1 - softTurnForwardRatio)

        self.newBearing = None
        self.newSoft = False

        self.shuttingDown = False
        self.motorsLock = Condition()
        self.motorsThread = Thread(daemon=True, target=self.motorsLoop)
        self.motorsThread.start()

    def motorsLoop(self):
        bearing = None
        soft = False

        while True:
            with self.motorsLock:
                if self.shuttingDown:
                    break

                if self.newBearing == bearing and self.newSoft == soft:
                    print("Motors going to sleep")
                    self.motorsLock.wait()

                if self.newBearing != bearing or self.newSoft != soft:
                    print("Motors woke up")

                    bearing = self.newBearing
                    soft = self.newSoft

                    leftDC = None
                    rightDC = None

                    if bearing == -1:
                        leftDC = 0
                        rightDC = 0
                    elif bearing == "n":
                        leftDC = 100
                        rightDC = 100
                    elif bearing == "ne":
                        leftDC = 100
                        rightDC = 100 * self.halfTurnSpeed
                    elif bearing == "e" and not soft:
                        leftDC = 100
                        rightDC = -100
                    elif bearing == "se":
                        leftDC = -100
                        rightDC = -100 * self.halfTurnSpeed
                    elif bearing == "s":
                        leftDC = -100
                        rightDC = -100
                    elif bearing == "sw":
                        leftDC = -100 * self.halfTurnSpeed
                        rightDC = -100
                    elif bearing == "w" and not soft:
                        leftDC = -100
                        rightDC = 100
                    elif bearing == "nw":
                        leftDC = 100 * self.halfTurnSpeed
                        rightDC = 100

                    if leftDC is not None and rightDC is not None:
                        self.leftMotor.setMotion(int(leftDC))
                        self.rightMotor.setMotion(int(rightDC))
                        self.motorsLock.wait()
                    elif (bearing == "e" or bearing == "w") and soft:
                        if bearing == "e":
                            forwardMotor = self.leftMotor
                            backwardsMotor = self.rightMotor
                        else:
                            forwardMotor = self.rightMotor
                            backwardsMotor = self.leftMotor

                        forwardMotor.setMotion(100)
                        while True:
                            backwardsMotor.setMotion(100)

                            changed = self.motorsLock.wait(self.softTurnForwardSec)
                            if changed:
                                break

                            backwardsMotor.setMotion(-100)
                            changed = self.motorsLock.wait(self.softTurnBackwardsSec)
                            if changed:
                                break
                    else:
                        # this code path should never be reached
                        raise Exception("Unable to determine bearing")

    def stop(self):
        with self.motorsLock:
            print("Waiting for motor thread to stop...")
            self.shuttingDown = True
            self.motorsLock.notify()

        print("Joining the timing thread")
        self.motorsThread.join()
        print("Motor thread stopped")

    def setBearing(self, bearing, soft):
        if bearing not in self.validBearings and bearing != -1:
            raise ValueError("Invalid bearing: {}".format(bearing))

        self.newBearing = bearing
        self.newSoft = soft

        with self.motorsLock:
            self.motorsLock.notify()




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
            self.stopping = True
            self.timingLock.notify()

        print("Joining the timing thread")
        self.timingThread.join()
        print("Servo thread stopped")

    def timingLoop(self):
        print("Servo starting...")

        # go neutral first
        self.pi.hardware_PWM(self.pwmPin, self.frequency, self.neutral)
        time.sleep(2)
        self.pi.hardware_PWM(self.pwmPin, self.frequency, 0)

        currentPosition = self.neutral
        lastChangeTime = -1

        while True:
            with self.timingLock:
                if not self.__shouldBeMoving(currentPosition):
                    self.pi.hardware_PWM(self.pwmPin, self.frequency, 0)
                    print("Servo idling...")
                    self.timingLock.wait()
                    print("Servo woke up...")

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


class Driver:

    def __init__(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.pi = pigpio.pi()
        print("Creating motor controller...")

        config = configparser.ConfigParser()
        config.read("rover.conf")

        driverConfig = config["DRIVER"]
        leftMotorConfig = config["LEFTMOTOR"]
        rightMotorConfig = config["RIGHTMOTOR"]
        servoConfig = config["SERVO"]

        leftMotor = Motor(self.pi, int(leftMotorConfig["PWMPin"]),
                            int(leftMotorConfig["ForwardPin"]),
                            int(leftMotorConfig["ReversePin"]),
                            float(leftMotorConfig["Trim"]))

        rightMotor = Motor(self.pi, int(rightMotorConfig["PWMPin"]),
                             int(rightMotorConfig["ForwardPin"]),
                             int(rightMotorConfig["ReversePin"]),
                             float(rightMotorConfig["Trim"]))

        self.motorController = MotorController(leftMotor,
                                               rightMotor,
                                               float(driverConfig["HalfTurnSpeed"]),
                                               float(driverConfig["SoftTurnForwardAssistRatio"]),
                                               float(driverConfig["SoftTurnPeriod"]))

        self.servoController = ServoController(self.pi, int(servoConfig["PWMPin"]))

    def setBearing(self, bearing, soft):
        self.motorController.setBearing(bearing, soft)

    def stop(self):
        self.motorController.setBearing(-1, False)

    def lookUp(self):
        self.servoController.backward()

    def lookDown(self):
        self.servoController.forward()

    def lookStop(self):
        self.servoController.lookStop()

    def cleanup(self):
        self.motorController.stop()
        self.servoController.stop()
        self.pi.stop()
