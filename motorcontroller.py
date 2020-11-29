from motor import Motor
import pigpio


class MotorController:
    validBearings = ["n", "ne", "e", "se", "s", "sw", "w", "nw", "0"]

    def __init__(self, config, gpio):
        driverConfig = config["DRIVER"]
        leftMotorConfig = config["LEFTMOTOR"]
        rightMotorConfig = config["RIGHTMOTOR"]

        leftMotor = Motor(
            gpio,
            int(leftMotorConfig["ForwardPin"]),
            int(leftMotorConfig["ReversePin"]),
            float(leftMotorConfig["Trim"])
        )

        rightMotor = Motor(
            gpio,
            int(rightMotorConfig["ForwardPin"]),
            int(rightMotorConfig["ReversePin"]),
            float(rightMotorConfig["Trim"])
        )

        self.leftMotor = leftMotor
        self.rightMotor = rightMotor
        self.halfTurnSpeed = float(driverConfig["HalfTurnSpeed"])
        self.slowSpeed = float(driverConfig["SlowSpeed"])
        self.enablePin = int(driverConfig["EnablePin"])
        self.gpio = gpio

        self.gpio.set_mode(self.enablePin, pigpio.OUTPUT)
        self.gpio.write(self.enablePin, pigpio.LOW)

    def getTargetMotorDCs(self, targetBearing, slow):
        if targetBearing == "0":
            leftDC = 0
            rightDC = 0
        elif targetBearing == "n":
            leftDC = 100
            rightDC = 100
        elif targetBearing == "ne":
            leftDC = 100
            rightDC = 100 * self.halfTurnSpeed
        elif targetBearing == "e":
            leftDC = 100
            rightDC = -100
        elif targetBearing == "se":
            leftDC = -100
            rightDC = -100 * self.halfTurnSpeed
        elif targetBearing == "s":
            leftDC = -100
            rightDC = -100
        elif targetBearing == "sw":
            leftDC = -100 * self.halfTurnSpeed
            rightDC = -100
        elif targetBearing == "w":
            leftDC = -100
            rightDC = 100
        elif targetBearing == "nw":
            leftDC = 100 * self.halfTurnSpeed
            rightDC = 100
        else:
            raise Exception("Bad bearing: " + targetBearing)

        if slow:
            leftDC = leftDC * self.slowSpeed
            rightDC = rightDC * self.slowSpeed

        return int(leftDC), int(rightDC)

    def setBearing(self, bearing, slow):
        if bearing not in self.validBearings:
            raise ValueError("Invalid bearing: {}".format(bearing))

        leftDC, rightDC = self.getTargetMotorDCs(bearing, slow)
        leftActive = self.leftMotor.setMotion(leftDC)
        rightActive = self.rightMotor.setMotion(rightDC)
        if leftActive or rightActive:
            self.gpio.write(self.enablePin, pigpio.HIGH)
        else:
            self.gpio.write(self.enablePin, pigpio.LOW)