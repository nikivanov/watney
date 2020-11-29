import pigpio

class Motor:
    PWM_FREQUENCY = 200

    def __init__(self, gpio, forwardPin, reversePin, trim):
        self.gpio = gpio
        self.forwardPin = forwardPin
        self.reversePin = reversePin
        self.trim = trim
        self.__initMotor()

    def __initMotor(self):
        self.gpio.set_PWM_frequency(self.forwardPin, self.PWM_FREQUENCY)
        self.gpio.set_PWM_range(self.forwardPin, 100)
        self.gpio.set_PWM_frequency(self.reversePin, self.PWM_FREQUENCY)
        self.gpio.set_PWM_range(self.reversePin, 100)
        self.stop()

    def stop(self):
        self.gpio.set_PWM_dutycycle(self.forwardPin, 0)
        self.gpio.set_PWM_dutycycle(self.reversePin, 0)

    def setMotion(self, dutyCycle):
        self.stop()
        if dutyCycle != 0:
            targetDC = int(abs(dutyCycle * self.trim))
            # below 50 DC, the motor will stall, which isn't good for anybody
            if targetDC > 50:
                if dutyCycle >= 0:
                    self.gpio.set_PWM_dutycycle(self.forwardPin, targetDC)
                else:
                    self.gpio.set_PWM_dutycycle(self.reversePin, targetDC)
                return True
            else:
                return False
            
            