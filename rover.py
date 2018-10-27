import configparser
import pigpio
from threading import Thread, Condition
import time
import os
import subprocess
import re
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

    def __init__(self, leftMotor, rightMotor, halfTurnSpeed):
        self.leftMotor = leftMotor
        self.rightMotor = rightMotor
        self.halfTurnSpeed = halfTurnSpeed

    def getTargetMotorDCs(self, targetBearing):
        if targetBearing == -1:
            leftDC = 0
            rightDC = 0
        elif targetBearing == "n":
            leftDC = 100
            rightDC = 100
        elif targetBearing == "ne":
            leftDC = 100
            rightDC = 100 * self.halfTurnSpeed
        elif targetBearing == "e":
            leftDC = 100
            rightDC = -100
        elif targetBearing == "se":
            leftDC = -100
            rightDC = -100 * self.halfTurnSpeed
        elif targetBearing == "s":
            leftDC = -100
            rightDC = -100
        elif targetBearing == "sw":
            leftDC = -100 * self.halfTurnSpeed
            rightDC = -100
        elif targetBearing == "w":
            leftDC = -100
            rightDC = 100
        elif targetBearing == "nw":
            leftDC = 100 * self.halfTurnSpeed
            rightDC = 100
        else:
            raise Exception("Bad bearing: " + targetBearing)

        return int(leftDC), int(rightDC)

    def setBearing(self, bearing):
        if bearing not in self.validBearings and bearing != -1:
            raise ValueError("Invalid bearing: {}".format(bearing))

        leftDC, rightDC = self.getTargetMotorDCs(bearing)
        self.leftMotor.setMotion(leftDC)
        self.rightMotor.setMotion(rightDC)


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
                                               float(driverConfig["HalfTurnSpeed"]))

        self.servoController = ServoController(self.pi, int(servoConfig["PWMPin"]))

        heartbeatInterval = float(driverConfig["MaxHeartbeatInvervalMS"])
        self.ssidRegex = re.compile(r"ESSID:\"(.+?)\"")
        self.qualityRegex = re.compile(r"Link Quality=([^ ]+)")
        self.signalRegex = re.compile(r"Signal level=(.*? dBm)")
        self.lastHeartbeat = time.time()
        self.heartbeatThread = Thread(daemon=True, target=self.heartbeatLoop, args=[heartbeatInterval])
        self.heartbeatThread.start()

    shuttingDown = False
    lastHeartbeat = -1
    heartbeatStop = False;
    lastHeartbeatData = {
                "SSID": "-",
                "Quality": "-",
                "Signal": "-"
            }

    def heartbeatLoop(self, maxInterval):
        print("Starting heartbeat thread...")
        while not self.shuttingDown:
            if (time.time() - self.lastHeartbeat) > maxInterval:
                if not self.heartbeatStop:
                    self.stop()
                    self.lookStop()
                    self.heartbeatStop = True
            else:
                self.heartbeatStop = False

            self.lastHeartbeatData = self.collectHeartbeatData()
            time.sleep(0.5)

    def collectHeartbeatData(self):
        try:
            wifiInfo = subprocess.check_output("iwconfig wlan0", shell=True).decode("utf-8")
            ssidMatch = self.ssidRegex.search(wifiInfo)
            ssid = ssidMatch.group(1) if ssidMatch else None

            qualityMatch = self.qualityRegex.search(wifiInfo)
            quality = qualityMatch.group(1) if qualityMatch else None

            signalMatch = self.signalRegex.search(wifiInfo)
            signal = signalMatch.group(1) if signalMatch else None

            return {
                "SSID": ssid,
                "Quality": quality,
                "Signal": signal
            }
        except Exception as ex:
            print(str(ex), file=sys.stderr)
            return {
                "SSID": "-",
                "Quality": "-",
                "Signal": "-"
            }

    def setBearing(self, bearing):
        self.motorController.setBearing(bearing)

    def stop(self):
        self.motorController.setBearing(-1)

    def lookUp(self):
        self.servoController.backward()

    def lookDown(self):
        self.servoController.forward()

    def lookStop(self):
        self.servoController.lookStop()

    def onHeartbeat(self):
        self.lastHeartbeat = time.time()
        return self.lastHeartbeatData

    def cleanup(self):
        self.servoController.stop()
        self.pi.stop()
        self.shuttingDown = True
        print("Waiting for heartbeat thread to stop...")
        self.heartbeatThread.join()
        print("Heartbeat thread stopped")
