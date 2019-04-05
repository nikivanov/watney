import pigpio


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