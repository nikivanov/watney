import time
from threading import Thread


import RPi.GPIO as GPIO


class Motor:

    def __init__(self, pins, reverse, rpms, rampUpTime):
        self.pins = pins
        self.runInReverse = reverse
        self.__setSequence()
        self.maxRPM = rpms
        self.bearing = -1
        self.rampUpTime = rampUpTime
        self.__initMotor()

    def __setSequence(self):
        # seq = [[1, 0, 0, 0],
        #        [1, 1, 0, 0],
        #        [0, 1, 0, 0],
        #        [0, 1, 1, 0],
        #        [0, 0, 1, 0],
        #        [0, 0, 1, 1],
        #        [0, 0, 0, 1],
        #        [1, 0, 0, 1]]
        # degreePerStep = 5.625

        seq = [[0, 0, 1, 1],
               [1, 0, 0, 1],
               [1, 1, 0, 0],
               [0, 1, 1, 0]]
        degreePerStep = 11.25

        gearRatio = 1/64
        realDegreePerStep = degreePerStep * gearRatio
        self.steps_per_rev = int(360 / realDegreePerStep)

        if self.runInReverse:
            seq.reverse()

        self.sequence = seq
        return seq

    def __initMotor(self):
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        self.__clear()

    def __clear(self):
        for pin in self.pins:
            GPIO.output(pin, 0)

    def setBearing(self, bearing):
        self.bearing = bearing

    def doDrive(self):
        print("Starting motor...")
        currentRPMs = 0
        # track last time actual speed change occured
        lastSpeedChange = -1
        # how much time to wait between each speed change, in seconds
        speedChangeTimeStep = self.rampUpTime / (self.maxRPM * 2)
        # Current step in sequence if rotating clockwise
        stepInSequence = 0
        lastMoveTime = -1
        currentSleep = -1
        while True:
            currentBearing = self.bearing
            '''
            0: left full forward, right stop
            45: left full forward, right half forward
            90: left full forward, right full forward
            135: left half forward, right full forward
            180: left stop, right full forward
            225: left half backward, right full backward
            270: left full backward, right full backward
            315: left full backward, right half backward 
            '''
            if currentBearing == -1:
                rpmFactor = 0
            elif currentBearing <= 90:
                if self.runInReverse:
                    rpmFactor = 1
                else:
                    rpmFactor = float(currentBearing) / 90
            elif currentBearing <= 180:
                if self.runInReverse:
                    rpmFactor = float(180 - currentBearing) / 90
                else:
                    rpmFactor = 1
            elif currentBearing <= 270:
                if self.runInReverse:
                    rpmFactor = float(currentBearing - 180) / 90
                else:
                    rpmFactor = 1
            else:
                if self.runInReverse:
                    rpmFactor = 1
                else:
                    rpmFactor = float(360 - self.bearing) / 90

            targetRPM = self.maxRPM * rpmFactor
            reversing = self.bearing > 180
            if reversing:
                targetRPM = targetRPM * -1

            if currentRPMs != targetRPM:
                if (time.time() - lastSpeedChange) > speedChangeTimeStep:
                    if currentRPMs < targetRPM:
                        currentRPMs = currentRPMs + 1
                    else:
                        currentRPMs = currentRPMs - 1
                    lastSpeedChange = time.time()
                    print("Current speed " + str(currentRPMs))

            if lastMoveTime != -1:
                sleepRemainder = currentSleep - (time.time() - lastMoveTime)
                if sleepRemainder > 0:
                    time.sleep(sleepRemainder)

            if currentRPMs == 0:
                currentSleep = 60 / self.steps_per_rev
                lastMoveTime = -1
                time.sleep(currentSleep)
            else:
                currentSleep = (60 / abs(currentRPMs)) / self.steps_per_rev
                step = self.sequence[stepInSequence]

                for pinIx in range(0, 4):
                    GPIO.output(self.pins[pinIx], step[pinIx] % 2)

                lastMoveTime = time.time()

                if currentRPMs < 0:
                    stepInSequence = stepInSequence - 1
                    if stepInSequence < 0:
                        stepInSequence = len(self.sequence) - 1
                elif currentRPMs > 0:
                    stepInSequence = stepInSequence + 1
                    if stepInSequence > 3:
                        stepInSequence = 0


class Driver:
    rpms = 18
    rampUpTime = 0.5

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        print("Creating motors...")
        self.motor1 = Motor([8, 10, 12, 11], False, self.rpms, self.rampUpTime)
        self.motor2 = Motor([36, 38, 40, 37], True, self.rpms, self.rampUpTime)
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

