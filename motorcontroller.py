from events import Events
from motor import Motor
import pigpio


class MotorController:
    validBearings = ["n", "ne", "e", "se", "s", "sw", "w", "nw", "0"]

    def __init__(self, config, gpio, audioManager):
        driverConfig = config["DRIVER"]
        leftMotorConfig = config["LEFTMOTOR"]
        rightMotorConfig = config["RIGHTMOTOR"]
        
        self.trim = float(driverConfig["Trim"])
        self.pwmFrequency = int(driverConfig["PWMFrequency"])

        leftMotor = Motor(
            gpio,
            self.pwmFrequency,
            int(leftMotorConfig["ForwardPin"]),
            int(leftMotorConfig["ReversePin"]),
            1 if self.trim >= 0 else 1 + self.trim,
            'Left Motor'
        )

        rightMotor = Motor(
            gpio,
            self.pwmFrequency,
            int(rightMotorConfig["ForwardPin"]),
            int(rightMotorConfig["ReversePin"]),
            1 if self.trim <= 0 else 1 - self.trim,
            'Right Motor'
        )

        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

        self.gpio = gpio

        self.straightaway = float(driverConfig["Straightaway"])
        self.straightawaySlow = float(driverConfig["StraightawaySlow"])
        self.halfTurnUndersteer = float(driverConfig["HalfTurnUndersteer"])
        self.halfTurnSlowFactor = float(driverConfig["HalfTurnSlowFactor"])
        self.tankTurnSpeed = float(driverConfig["TankTurnSpeed"])
        self.tankTurnSpeedSlow = float(driverConfig["TankTurnSpeedSlow"])
        
        self.enablePin = int(driverConfig["EnablePin"])

        self.gpio.set_mode(self.enablePin, pigpio.OUTPUT)
        self.gpio.write(self.enablePin, pigpio.LOW)

        self.audioManager = audioManager
        self.audioToken = 'fe7a1846-a0bb-4a44-aa3e-5b080089d37a'

    def getTargetMotorDCs(self, targetBearing, slow):
        if targetBearing == "0":
            leftDC = 0
            rightDC = 0
        elif targetBearing == "n":
            if not slow:
                leftDC = 100 * self.straightaway
                rightDC = 100 * self.straightaway
            else:
                leftDC = 100 * self.straightawaySlow
                rightDC = 100 * self.straightawaySlow
        elif targetBearing == "ne":
            if not slow:
                leftDC = 100
                rightDC = 100 * self.halfTurnUndersteer
            else:
                leftDC = 100 * self.halfTurnSlowFactor
                rightDC = 100 * self.halfTurnUndersteer * self.halfTurnSlowFactor
        elif targetBearing == "e":
            if not slow:
                leftDC = 100 * self.tankTurnSpeed
                rightDC = -100 * self.tankTurnSpeed
            else:
                leftDC = 100 * self.tankTurnSpeedSlow
                rightDC = -100 * self.tankTurnSpeedSlow
        elif targetBearing == "se":
            if not slow:
                leftDC = -100
                rightDC = -100 * self.halfTurnUndersteer
            else:
                leftDC = -100 * self.halfTurnSlowFactor
                rightDC = -100 * self.halfTurnUndersteer * self.halfTurnSlowFactor
        elif targetBearing == "s":
            if not slow:
                leftDC = -100 * self.straightaway
                rightDC = -100 * self.straightaway
            else:
                leftDC = -100 * self.straightawaySlow
                rightDC = -100 * self.straightawaySlow
        elif targetBearing == "sw":
            if not slow:
                leftDC = -100 * self.halfTurnUndersteer
                rightDC = -100  
            else:
                leftDC = -100 * self.halfTurnUndersteer * self.halfTurnSlowFactor
                rightDC = -100 * self.halfTurnSlowFactor
        elif targetBearing == "w":
            if not slow:
                leftDC = -100 * self.tankTurnSpeed
                rightDC = 100 * self.tankTurnSpeed
            else:
                leftDC = -100 * self.tankTurnSpeedSlow
                rightDC = 100 * self.tankTurnSpeedSlow
        elif targetBearing == "nw":
            if not slow:
                leftDC = 100 * self.halfTurnUndersteer
                rightDC = 100
            else:
                leftDC = 100 * self.halfTurnUndersteer * self.halfTurnSlowFactor
                rightDC = 100 * self.halfTurnSlowFactor
        else:
            raise Exception("Bad bearing: " + targetBearing)

        return int(leftDC), int(rightDC)

    def setBearing(self, bearing, slow):
        if bearing not in self.validBearings:
            raise ValueError("Invalid bearing: {}".format(bearing))

        leftDC, rightDC = self.getTargetMotorDCs(bearing, slow)
        leftActive = self.leftMotor.setMotion(leftDC)
        rightActive = self.rightMotor.setMotion(rightDC)
        if leftActive or rightActive:
            self.gpio.write(self.enablePin, pigpio.HIGH)
            self.audioManager.lowerVolume(self.audioToken)
            Events.getInstance().fireMotionOn()
        else:
            self.gpio.write(self.enablePin, pigpio.LOW)
            self.audioManager.restoreVolume(self.audioToken)
            Events.getInstance().fireMotionOff()