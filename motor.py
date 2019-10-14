import RPi.GPIO as GPIO

class Motor:
    PWM_FREQUENCY = 200

    def __init__(self, pwmPin, forwardPin, reversePin, trim):
        self.pwmPin = pwmPin
        self.forwardPin = forwardPin
        self.reversePin = reversePin
        self.pwmControl = None
        self.trim = trim
        self.__initMotor()

    def __initMotor(self):
        GPIO.setup(self.forwardPin, GPIO.OUT)
        GPIO.setup(self.reversePin, GPIO.OUT)
        GPIO.setup(self.pwmPin, GPIO.OUT)

        self.pwmControl = GPIO.PWM(self.pwmPin, self.PWM_FREQUENCY)
        self.pwmControl.start(0)
        self.stop()

    def stop(self):
        GPIO.output(self.forwardPin, GPIO.LOW)
        GPIO.output(self.reversePin, GPIO.LOW)
        self.pwmControl.ChangeDutyCycle(0)

    def setMotion(self, dutyCycle):
        self.stop()

        if dutyCycle != 0:
            if dutyCycle >= 0:
                GPIO.output(self.forwardPin, GPIO.HIGH)
            else:
                GPIO.output(self.reversePin, GPIO.HIGH)

            targetDC = int(abs(dutyCycle * self.trim))

            # below 20 DC, the motor will stall, which isn't good for anybody
            if targetDC > 20:
                self.pwmControl.ChangeDutyCycle(targetDC)
            else:
                self.pwmControl.ChangeDutyCycle(0)