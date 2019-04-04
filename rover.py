import os
from motor import Motor
from motorcontroller import MotorController
from servocontroller import ServoController

class Driver:

    def __init__(self, config, pi):
        # os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.pi = pi

        # videoConfig = config["VIDEO"]
        driverConfig = config["DRIVER"]
        leftMotorConfig = config["LEFTMOTOR"]
        rightMotorConfig = config["RIGHTMOTOR"]
        servoConfig = config["SERVO"]

        print("Creating motor controller...")

        leftMotor = Motor(self.pi, int(leftMotorConfig["PWMPin"]),
                          int(leftMotorConfig["ForwardPin"]),
                          int(leftMotorConfig["ReversePin"]),
                          float(leftMotorConfig["Trim"]))

        rightMotor = Motor(self.pi, int(rightMotorConfig["PWMPin"]),
                           int(rightMotorConfig["ForwardPin"]),
                           int(rightMotorConfig["ReversePin"]),
                           float(rightMotorConfig["Trim"]))

        self.motorController = MotorController(leftMotor,
                                               rightMotor,
                                               float(driverConfig["HalfTurnSpeed"]))

        self.servoController = ServoController(self.pi, int(servoConfig["PWMPin"]))

    def setBearing(self, bearing):
        self.motorController.setBearing(bearing)

    def stop(self):
        self.motorController.setBearing(-1)

    def lookUp(self):
        self.servoController.backward()

    def lookDown(self):
        self.servoController.forward()

    def lookStop(self):
        self.servoController.lookStop()

    def cleanup(self):
        self.servoController.stop()
