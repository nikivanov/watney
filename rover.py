import time
from threading import Thread
from time import sleep

import RPi.GPIO as GPIO


class Motor:

    def __init__(self, pins, reverse, timeRes, rpms, rampUpTimeMS):
        self.pins = pins
        self.runInReverse = reverse

        self.maxRPM = rpms
        self.bearing = -1
        self.timeRes = timeRes
        self.currentBearing = -1
        self.bearingSetTime = -1
        self.rampUpTimeMS = rampUpTimeMS
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
        reverseSequence = list(seq)
        reverseSequence.reverse()
        self.reverseSequence = reverseSequence

        return seq

    def __initMotor(self):
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        self.__clear()

    def __clear(self):
        for pin in self.pins:
            GPIO.output(pin, 0)

    def setBearing(self, bearing):
        if self.currentBearing != bearing:
            self.bearingSetTime = time.time()

        self.currentBearing = bearing
        self.bearing = bearing

    def doDrive(self):
        print("Starting motor...")
        while True:
            if self.bearing == -1:
                self.__clear()
                sleep(self.timeRes)

            else:
                reversing = self.bearing > 180

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

                if self.bearing <= 90:
                    if self.runInReverse:
                        rpmFactor = 1
                    else:
                        rpmFactor = float(self.bearing) / 90
                elif self.bearing <= 180:
                    if self.runInReverse:
                        rpmFactor = float(180 - self.bearing) / 90
                    else:
                        rpmFactor = 1
                elif self.bearing <= 270:
                    if self.runInReverse:
                        rpmFactor = float(self.bearing - 180) / 90
                    else:
                        rpmFactor = 1
                else:
                    if self.runInReverse:
                        rpmFactor = 1
                    else:
                        rpmFactor = float(360 - self.bearing) / 90

                baseRPM = self.maxRPM * rpmFactor

                if baseRPM == 0:
                    self.bearing = -1
                else:
                    startTime = time.time()
                    seq = self.reverseSequence if reversing else self.sequence
                    while (time.time() - startTime) < self.timeRes:
                        for step in seq:
                            for pinIx in range(0, 4):
                                GPIO.output(self.pins[pinIx], step[pinIx] % 2)

                            rampUpFactor = min((time.time() - self.bearingSetTime) / self.rampUpTimeMS, 1)
                            effectiveRPM = max(baseRPM * rampUpFactor, 1)
                            currentSleep = (60 / effectiveRPM) / self.steps_per_rev
                            sleep(currentSleep)


class Driver:

    timeResUnit = 0.2
    rpms = 18
    rampUpTimeMS = 500

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        print("Creating motors...")
        self.motor1 = Motor([8, 10, 12, 11], False, self.timeResUnit, self.rpms, self.rampUpTimeMS)
        self.motor2 = Motor([36, 38, 40, 37], True, self.timeResUnit, self.rpms, self.rampUpTimeMS)
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

