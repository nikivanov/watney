from motor import Motor


class MotorController:
    validBearings = ["n", "ne", "e", "se", "s", "sw", "w", "nw", "0"]

    def __init__(self, pi, config):
        driverConfig = config["DRIVER"]
        leftMotorConfig = config["LEFTMOTOR"]
        rightMotorConfig = config["RIGHTMOTOR"]

        leftMotor = Motor(pi, int(leftMotorConfig["PWMPin"]),
                          int(leftMotorConfig["ForwardPin"]),
                          int(leftMotorConfig["ReversePin"]),
                          float(leftMotorConfig["Trim"]))

        rightMotor = Motor(pi, int(rightMotorConfig["PWMPin"]),
                           int(rightMotorConfig["ForwardPin"]),
                           int(rightMotorConfig["ReversePin"]),
                           float(rightMotorConfig["Trim"]))

        self.leftMotor = leftMotor
        self.rightMotor = rightMotor
        self.halfTurnSpeed = float(driverConfig["HalfTurnSpeed"])

    def getTargetMotorDCs(self, targetBearing):
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

        return int(leftDC), int(rightDC)

    def setBearing(self, bearing):
        if bearing not in self.validBearings:
            raise ValueError("Invalid bearing: {}".format(bearing))

        leftDC, rightDC = self.getTargetMotorDCs(bearing)
        self.leftMotor.setMotion(leftDC)
        self.rightMotor.setMotion(rightDC)