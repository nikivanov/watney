import RPi.GPIO as GPIO

class Motor:
    PWM_FREQUENCY = 200

    def __init__(self, forwardPin, reversePin, trim):
        self.forwardPin = forwardPin
        self.reversePin = reversePin
        self.forwardPwm = None
        self.reversePwm = None
        self.trim = trim
        self.__initMotor()

    def __initMotor(self):
        GPIO.setup(self.forwardPin, GPIO.OUT)
        GPIO.setup(self.reversePin, GPIO.OUT)

        self.forwardPwm = GPIO.PWM(self.forwardPin, self.PWM_FREQUENCY)
        self.reversePwm = GPIO.PWM(self.reversePin, self.PWM_FREQUENCY)
        self.forwardPwm.start(0)
        self.reversePwm.start(0)
        self.stop()

    def stop(self):
        self.forwardPwm.ChangeDutyCycle(0)
        self.reversePwm.ChangeDutyCycle(0)

    def setMotion(self, dutyCycle):
        self.stop()

        if dutyCycle != 0:
            targetDC = int(abs(dutyCycle * self.trim))
            # below 20 DC, the motor will stall, which isn't good for anybody
            if targetDC > 20:
                if dutyCycle >= 0:
                    self.forwardPwm.ChangeDutyCycle(targetDC)
                else:
                    self.reversePwm.ChangeDutyCycle(targetDC)
                return True
            else:
                return False
            
            