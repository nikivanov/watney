import RPi.GPIO as GPIO


class Motor:
    PWM_FREQUENCY = 100

    def __init__(self, isLeft, pwmPin, forwardPin, reversePin, rampUpTime, trim):
        self.isLeft = isLeft
        self.pwmPin = pwmPin
        self.forwardPin = forwardPin
        self.reversePin = reversePin
        self.targetBearing = -1
        self.targetSpeed = 0
        self.rampUpTime = rampUpTime
        self.pwmControl = None
        self.trim = trim
        self.__initMotor()

    def __initMotor(self):
        GPIO.setup(self.pwmPin, GPIO.OUT)
        GPIO.setup(self.forwardPin, GPIO.OUT)
        GPIO.setup(self.reversePin, GPIO.OUT)
        self.pwmControl = GPIO.PWM(self.pwmPin, self.PWM_FREQUENCY)
        self.pwmControl.start(100)
        self.__clear()

    def __clear(self):
        GPIO.output(self.forwardPin, 0)
        GPIO.output(self.reversePin, 0)

    def setBearing(self, bearing, speed):
        self.targetBearing = bearing
        self.targetSpeed = speed
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

        if rpmFactor < 1 and speed == 1:
            rpmFactor = rpmFactor * understeer

        targetDC = 100 * speed * rpmFactor * self.trim

        if targetDC > 20:
            self.pwmControl.ChangeDutyCycle(targetDC)
            if reversing:
                GPIO.output(self.reversePin, 1)
            else:
                GPIO.output(self.forwardPin, 1)


class Driver:
    maxDC = 100
    rampUpTime = 0.5

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        print("Creating motors...")
        self.motor1 = Motor(True, 16, 18, 22, self.rampUpTime, 1)
        self.motor2 = Motor(False, 15, 13, 11, self.rampUpTime, 0.9)

    def setBearing(self, bearing, speed):
        if bearing < 0 or bearing > 359:
            raise ValueError("Invalid bearing: " + bearing)

        if speed < 0 or speed > 1:
            raise ValueError("Invalid speed: " + speed)

        self.motor1.setBearing(bearing, speed)
        self.motor2.setBearing(bearing, speed)

    def stop(self):
        self.motor1.setBearing(-1, 0)
        self.motor2.setBearing(-1, 0)

    def cleanup(self):
        GPIO.cleanup()

