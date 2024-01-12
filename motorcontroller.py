from events import Events
from motor import Motor
import pigpio


class MotorController:
    validBearings = ["n", "ne", "e", "se", "s", "sw", "w", "nw", "0"]

    def __init__(self, config, gpio, audioManager, steerController):
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

        self.steer = steerController

    def getTargetMotorDCsAndSteer(self, targetBearing, slow):
        if targetBearing == "0":
            leftDC = 0
            rightDC = 0
            steer = 0
        elif targetBearing == "n":
            if not slow:
                leftDC = 100 * self.straightaway
                rightDC = 100 * self.straightaway
            else:
                leftDC = 100 * self.straightawaySlow
                rightDC = 100 * self.straightawaySlow
            steer = 0
        elif targetBearing == "ne":
            steer = 1
            if not slow:
                leftDC = 100 * self.straightaway
                rightDC = 100 * self.straightaway
            else:
                leftDC = 100 * self.straightawaySlow
                rightDC = 100 * self.straightawaySlow
        elif targetBearing == "e":
            steer = 1
            leftDC = 0
            rightDC = 0
        elif targetBearing == "se":
            steer = 1
            if not slow:
                leftDC = -100 * self.straightaway
                rightDC = -100 * self.straightaway
            else:
                leftDC = -100 * self.straightawaySlow
                rightDC = -100 * self.straightawaySlow
        elif targetBearing == "s":
            steer = 0
            if not slow:
                leftDC = -100 * self.straightaway
                rightDC = -100 * self.straightaway
            else:
                leftDC = -100 * self.straightawaySlow
                rightDC = -100 * self.straightawaySlow
        elif targetBearing == "sw":
            steer = -1
            if not slow:
                leftDC = -100 * self.straightaway
                rightDC = -100 * self.straightaway
            else:
                leftDC = -100 * self.straightawaySlow
                rightDC = -100 * self.straightawaySlow
        elif targetBearing == "w":
            steer = -1
            leftDC = 0
            rightDC = 0
        elif targetBearing == "nw":
            steer = -1
            if not slow:
                leftDC = 100 * self.straightaway
                rightDC = 100 * self.straightaway
            else:
                leftDC = 100 * self.straightawaySlow
                rightDC = 100 * self.straightawaySlow
        else:
            raise Exception("Bad bearing: " + targetBearing)

        return int(leftDC), int(rightDC), steer

    def setBearing(self, bearing, slow):
        if bearing not in self.validBearings:
            raise ValueError("Invalid bearing: {}".format(bearing))

        leftDC, rightDC, steer = self.getTargetMotorDCsAndSteer(bearing, slow)
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

        if steer < 0:
            self.steer.left()
        elif steer > 0:
            self.steer.right()
        else:
            self.steer.center()
