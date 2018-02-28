import RPi.GPIO as GPIO
import configparser
from threading import Thread, Condition
import time


class Motor:
    PWM_FREQUENCY = 100

    def __init__(self, pwmPin, forwardPin, reversePin, trim):
        self.pwmPin = pwmPin
        self.forwardPin = forwardPin
        self.reversePin = reversePin
        self.pwmControl = None
        self.trim = trim
        self.__initMotor()

    def __initMotor(self):
        GPIO.setup(self.pwmPin, GPIO.OUT)
        GPIO.setup(self.forwardPin, GPIO.OUT)
        GPIO.setup(self.reversePin, GPIO.OUT)
        self.pwmControl = GPIO.PWM(self.pwmPin, self.PWM_FREQUENCY)
        self.pwmControl.start(100)
        self.stop()

    def stop(self):
        GPIO.output(self.forwardPin, 0)
        GPIO.output(self.reversePin, 0)

    def setMotion(self, dutyCycle):
        self.stop()

        if dutyCycle != 0:
            if dutyCycle >= 0:
                GPIO.output(self.forwardPin, 1)
            else:
                GPIO.output(self.reversePin, 1)

            targetDC = abs(dutyCycle * self.trim)

            # below 20 DC, the motor will stall, which isn't good for anybody
            if targetDC > 20:
                self.pwmControl.ChangeDutyCycle(targetDC)
            else:
                self.pwmControl.ChangeDutyCycle(0)


class MotorController:

    def __init__(self, leftMotors, rightMotors, fullCycleRampUp):
        self.leftMotors = leftMotors
        self.rightMotors = rightMotors

        self.speedChangeInterval = 0.1
        self.dcChangePerInterval = (200 * self.speedChangeInterval) / fullCycleRampUp

        self.speedThreadSync = Condition()
        self.targetSpeed = 0
        self.targetBearing = -1
        self.speedChangeThread = Thread(target=self.speedChangeLoop, daemon=True)
        self.speedChangeThread.start()

    def speedChangeLoop(self):
        currentLeftDC = 0
        currentRightDC = 0

        while True:
            with self.speedThreadSync:
                targetDCs = self.getTargetMotorDCs(self.targetBearing, self.targetSpeed)
                if currentLeftDC == targetDCs[0] and currentRightDC == targetDCs[1]:
                    print("Target speeds reached, sleeping...")
                    self.speedThreadSync.wait()
                targetDCs = self.getTargetMotorDCs(self.targetBearing, self.targetSpeed)

            changesPerCycle = self.getDCChangePerCycle(targetDCs, currentLeftDC, currentRightDC)

            if currentLeftDC > targetDCs[0]:
                currentLeftDC = max(currentLeftDC - changesPerCycle[0], targetDCs[0])
            elif currentLeftDC < targetDCs[0]:
                currentLeftDC = min(currentLeftDC + changesPerCycle[0], targetDCs[0])

            if currentRightDC > targetDCs[1]:
                currentRightDC = max(currentRightDC - changesPerCycle[1], targetDCs[1])
            elif currentRightDC < targetDCs[1]:
                currentRightDC = min(currentRightDC + changesPerCycle[1], targetDCs[1])

            print("New left DC: {}".format(currentLeftDC))
            for motor in self.leftMotors:
                motor.setMotion(int(currentLeftDC))

            print("New right DC: {}".format(currentRightDC))
            for motor in self.rightMotors:
                motor.setMotion(int(currentRightDC))

            time.sleep(self.speedChangeInterval)

    def getDCChangePerCycle(self, targetDCs, currentLeftDC, currentRightDC):
        deltaLeftDC = abs(targetDCs[0] - currentLeftDC)
        deltaRightDC = abs(targetDCs[1] - currentRightDC)
        maxDelta = max(deltaLeftDC, deltaRightDC)

        steps = maxDelta / self.dcChangePerInterval

        if steps > 0:
            leftDCChangePerCycle = deltaLeftDC / steps
            rightDCChangePerCycle = deltaRightDC / steps
        else:
            leftDCChangePerCycle = 0
            rightDCChangePerCycle = 0

        return leftDCChangePerCycle, rightDCChangePerCycle

    def getTargetMotorDCs(self, targetBearing, targetSpeed):
        if targetBearing == -1:
            leftDC = 0
            rightDC = 0
        elif targetBearing <= 90:
            leftDC = 100
            rightDC = float(targetBearing) / 90 * 100
        elif targetBearing <= 180:
            leftDC = float(180 - targetBearing) / 90 * 100
            rightDC = 100
        elif targetBearing <= 270:
            leftDC = float(targetBearing - 180) / 90 * 100
            rightDC = 100
        else:
            leftDC = 100
            rightDC = float(360 - targetBearing) / 90 * 100

        if targetSpeed == 1:
            understeer = 0.8
            if leftDC < 100:
                leftDC = leftDC * understeer
            if rightDC < 100:
                rightDC = rightDC * understeer

        leftDC = leftDC * targetSpeed
        rightDC = rightDC * targetSpeed

        reversing = targetBearing > 180
        if reversing:
            leftDC = leftDC * -1
            rightDC = rightDC * -1

        return int(leftDC), int(rightDC)

    def setBearing(self, bearing, speed):
        if (bearing < 0 or bearing > 359) and bearing != -1:
            raise ValueError("Invalid bearing: {}".format(bearing))

        if speed < 0 or speed > 1:
            raise ValueError("Invalid speed: {}".format(speed))

        with self.speedThreadSync:
            self.targetBearing = bearing
            self.targetSpeed = speed
            self.speedThreadSync.notify()


class Driver:

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

        print("Creating motor controller...")

        config = configparser.ConfigParser()
        config.read("rover.conf")

        generalConfig = config["GENERAL"]
        leftMotorConfig = config["LEFTMOTOR"]
        rightMotorConfig = config["RIGHTMOTOR"]

        leftMotors = [Motor(int(leftMotorConfig["PWMPin"]),
                            int(leftMotorConfig["ForwardPin"]),
                            int(leftMotorConfig["ReversePin"]),
                            float(leftMotorConfig["Trim"]))]

        rightMotors = [Motor(int(rightMotorConfig["PWMPin"]),
                            int(rightMotorConfig["ForwardPin"]),
                            int(rightMotorConfig["ReversePin"]),
                            float(rightMotorConfig["Trim"]))]

        fullCycleRampUp = float(generalConfig["FullCycleRampUp"])

        self.controller = MotorController(leftMotors, rightMotors, fullCycleRampUp)

    def setBearing(self, bearing, speed):
        self.controller.setBearing(bearing, speed)

    def stop(self):
        self.controller.setBearing(-1, 0)

    def cleanup(self):
        GPIO.cleanup()

