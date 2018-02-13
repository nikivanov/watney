import time
from threading import Thread, Lock


import RPi.GPIO as GPIO


class Motor:
    PWM_FREQUENCY = 100

    def __init__(self, isLeft, pwmPin, forwardPin, reversePin, maxDC, rampUpTime):
        self.isLeft = isLeft
        self.pwmPin = pwmPin
        self.forwardPin = forwardPin
        self.reversePin = reversePin
        self.maxDC = maxDC
        self.targetBearing = -1
        self.rampUpTime = rampUpTime
        self.pwmControl = None
        self.__initMotor()

    def __initMotor(self):
        GPIO.setup(self.pwmPin, GPIO.OUT)
        GPIO.setup(self.forwardPin, GPIO.OUT)
        GPIO.setup(self.reversePin, GPIO.OUT)
        self.pwmControl = GPIO.PWM(self.pwmPin, self.PWM_FREQUENCY)
        self.pwmControl.start(self.maxDC)
        self.__clear()

    def __clear(self):
        GPIO.output(self.forwardPin, 0)
        GPIO.output(self.reversePin, 0)

    def setBearing(self, bearing):
        self.targetBearing = bearing
        self.__clear()

        currentBearing = bearing
        reversing = currentBearing > 180

        understeer = 0.8

        if currentBearing == -1:
            rpmFactor = 0
        elif currentBearing <= 90:
            if self.isLeft:
                rpmFactor = 1
            else:
                rpmFactor = float(currentBearing) / 90
        elif currentBearing <= 180:
            if self.isLeft:
                rpmFactor = float(180 - currentBearing) / 90
            else:
                rpmFactor = 1
        elif currentBearing <= 270:
            if self.isLeft:
                rpmFactor = float(currentBearing - 180) / 90
            else:
                rpmFactor = 1
        else:
            if self.isLeft:
                rpmFactor = 1
            else:
                rpmFactor = float(360 - currentBearing) / 90

        if rpmFactor < 1:
            rpmFactor = rpmFactor * understeer

        targetDC = self.maxDC * rpmFactor

        if targetDC > 20:
            self.pwmControl.ChangeDutyCycle(targetDC)
            if reversing:
                GPIO.output(self.reversePin, 1)
            else:
                GPIO.output(self.forwardPin, 1)




    def doDrive(self):
        return
        # print("Starting motor...")
        # currentDC = 0
        #
        # # track last time actual speed change occured
        # lastSpeedChange = -1
        #
        # # go from 0 to maxDC in rampUpTime seconds
        # # determines how fast we're changing duty cycles as we're ramping up to maxDC
        # dcChangeSpeed = self.maxDC / self.rampUpTime
        #
        # # Current step in sequence if rotating clockwise
        # lastMoveTime = -1
        # currentSleep = -1
        #
        # while True:
        #     currentBearing = self.bearing
        #     '''
        #     0: left full forward, right stop
        #     45: left full forward, right half forward
        #     90: left full forward, right full forward
        #     135: left half forward, right full forward
        #     180: left stop, right full forward
        #     225: left half backward, right full backward
        #     270: left full backward, right full backward
        #     315: left full backward, right half backward
        #     '''
        #     if currentBearing == -1:
        #         rpmFactor = 0
        #     elif currentBearing <= 90:
        #         if self.runInReverse:
        #             rpmFactor = 1
        #         else:
        #             rpmFactor = float(currentBearing) / 90
        #     elif currentBearing <= 180:
        #         if self.runInReverse:
        #             rpmFactor = float(180 - currentBearing) / 90
        #         else:
        #             rpmFactor = 1
        #     elif currentBearing <= 270:
        #         if self.runInReverse:
        #             rpmFactor = float(currentBearing - 180) / 90
        #         else:
        #             rpmFactor = 1
        #     else:
        #         if self.runInReverse:
        #             rpmFactor = 1
        #         else:
        #             rpmFactor = float(360 - self.bearing) / 90
        #
        #     targetRPM = self.maxRPM * rpmFactor
        #     reversing = self.bearing > 180
        #     if reversing:
        #         targetRPM = targetRPM * -1
        #
        #     if currentRPMs != targetRPM:
        #         if (time.time() - lastSpeedChange) > speedChangeTimeStep:
        #             if currentRPMs < targetRPM:
        #                 currentRPMs = currentRPMs + 1
        #             else:
        #                 currentRPMs = currentRPMs - 1
        #             lastSpeedChange = time.time()
        #             print("Current speed " + str(currentRPMs))
        #
        #     if lastMoveTime != -1:
        #         sleepRemainder = currentSleep - (time.time() - lastMoveTime)
        #         if sleepRemainder > 0:
        #             time.sleep(sleepRemainder)
        #
        #     if currentRPMs == 0:
        #         currentSleep = 60 / self.steps_per_rev
        #         lastMoveTime = -1
        #         self.__clear()
        #         time.sleep(currentSleep)
        #     else:
        #         currentSleep = (60 / abs(currentRPMs)) / self.steps_per_rev
        #         step = self.sequence[stepInSequence]
        #
        #         for pinIx in range(0, 4):
        #             GPIO.output(self.pins[pinIx], step[pinIx] % 2)
        #
        #         lastMoveTime = time.time()
        #
        #         if currentRPMs < 0:
        #             stepInSequence = stepInSequence - 1
        #             if stepInSequence < 0:
        #                 stepInSequence = len(self.sequence) - 1
        #         elif currentRPMs > 0:
        #             stepInSequence = stepInSequence + 1
        #             if stepInSequence > 3:
        #                 stepInSequence = 0


class Driver:
    maxDC = 100
    rampUpTime = 0.5

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        print("Creating motors...")
        self.motor1 = Motor(True, 16, 18, 22, self.maxDC, self.rampUpTime)
        self.motor2 = Motor(False, 15, 13, 11, self.maxDC, self.rampUpTime)
        self.__startDriverThreads()

    def __startDriverThreads(self):
        print("Starting motor threads...")
        self.motor1Thread = Thread(target=self.motor1.doDrive, daemon=True)
        self.motor2Thread = Thread(target=self.motor2.doDrive, daemon=True)
        self.motor1Thread.start()
        self.motor2Thread.start()

    def setBearing(self, bearing):
        if bearing < 0 or bearing > 359:
            raise ValueError("Invalid bearing: " + bearing)

        self.motor1.setBearing(bearing)
        self.motor2.setBearing(bearing)

    def stop(self):
        self.motor1.setBearing(-1)
        self.motor2.setBearing(-1)

    def cleanup(self):
        GPIO.cleanup()

