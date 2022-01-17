class Motor:
    def __init__(self, gpio, pwmFrequency, forwardPin, reversePin, trimOffset, name):
        self.gpio = gpio
        self.pwmFrequency = pwmFrequency
        self.forwardPin = forwardPin
        self.reversePin = reversePin
        self.trimOffset = trimOffset
        self.name = name
        self.__initMotor()

    def __initMotor(self):
        self.gpio.set_PWM_frequency(self.forwardPin, self.pwmFrequency)
        self.gpio.set_PWM_range(self.forwardPin, 100)
        self.gpio.set_PWM_frequency(self.reversePin, self.pwmFrequency)
        self.gpio.set_PWM_range(self.reversePin, 100)
        self.stop()

    def stop(self):
        self.gpio.set_PWM_dutycycle(self.forwardPin, 0)
        self.gpio.set_PWM_dutycycle(self.reversePin, 0)

    def setMotion(self, dutyCycle):
        self.stop()
        if dutyCycle != 0:
            trimmedDutyCycle = dutyCycle * self.trimOffset
            # print(self.name + ": " + str(trimmedDutyCycle))
            if trimmedDutyCycle > 0:
                self.gpio.set_PWM_dutycycle(self.forwardPin, trimmedDutyCycle)
            else:
                self.gpio.set_PWM_dutycycle(self.reversePin, trimmedDutyCycle * -1)
            return True
        else:
            return False
            
            