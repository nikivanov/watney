class SteerController:
    def __init__(self, gpio, config) -> None:
        steerConfig = config["STEER"]
        self.pwmPin = int(steerConfig["PWMPin"])
        self.neutral = int(steerConfig["Neutral"])
        self.amplitude = int(steerConfig["Amplitude"])
        self.invert = steerConfig["Invert"].lower() == "true"
        self.gpio = gpio
        self.center()
        
    def left(self):
        if self.invert:
            self.gpio.set_servo_pulsewidth(self.pwmPin, self.neutral + self.amplitude)
        else:
            self.gpio.set_servo_pulsewidth(self.pwmPin, self.neutral - self.amplitude)

    def right(self):
        if self.invert:
            self.gpio.set_servo_pulsewidth(self.pwmPin, self.neutral - self.amplitude)
        else:
            self.gpio.set_servo_pulsewidth(self.pwmPin, self.neutral + self.amplitude)
    
    def center(self):
        self.gpio.set_servo_pulsewidth(self.pwmPin, self.neutral)