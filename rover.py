import RPi.GPIO as GPIO
import configparser
import pigpio
from threading import Thread, Condition
import time


class Motor:
    PWM_FREQUENCY = 30

    def __init__(self, pwmPin, forwardPin, reversePin, trim):
        self.pwmPin = pwmPin
        self.forwardPin = forwardPin
        self.reversePin = reversePin
        self.pwmControl = None
        self.trim = trim
        self.__initMotor()

    def __initMotor(self):
        GPIO.setup(self.pwmPin, GPIO.OUT)
        GPIO.setup(self.forwardPin, GPIO.OUT)
        GPIO.setup(self.reversePin, GPIO.OUT)
        self.pwmControl = GPIO.PWM(self.pwmPin, self.PWM_FREQUENCY)
        self.pwmControl.start(100)
        self.stop()

    def stop(self):
        GPIO.output(self.forwardPin, 0)
        GPIO.output(self.reversePin, 0)

    def setMotion(self, dutyCycle):
        self.stop()

        if dutyCycle != 0:
            if dutyCycle >= 0:
                GPIO.output(self.forwardPin, 1)
            else:
                GPIO.output(self.reversePin, 1)

            targetDC = abs(dutyCycle * self.trim)

            # below 20 DC, the motor will stall, which isn't good for anybody
            if targetDC > 20:
                self.pwmControl.ChangeDutyCycle(targetDC)
            else:
                self.pwmControl.ChangeDutyCycle(0)


class MotorController:

    def __init__(self, leftMotors, rightMotors):
        self.leftMotors = leftMotors
        self.rightMotors = rightMotors

    def getTargetMotorDCs(self, targetBearing, targetSpeed):
        if targetBearing == -1:
            leftDC = 0
            rightDC = 0
        elif targetBearing <= 90:
            leftDC = 100
            rightDC = float(targetBearing) / 90 * 100
        elif targetBearing <= 180:
            leftDC = float(180 - targetBearing) / 90 * 100
            rightDC = 100
        elif targetBearing <= 270:
            leftDC = float(targetBearing - 180) / 90 * 100
            rightDC = 100
        else:
            leftDC = 100
            rightDC = float(360 - targetBearing) / 90 * 100

        if targetSpeed == 1:
            understeer = 0.8
            if leftDC < 100:
                leftDC = leftDC * understeer
            if rightDC < 100:
                rightDC = rightDC * understeer

        leftDC = leftDC * targetSpeed
        rightDC = rightDC * targetSpeed

        reversing = targetBearing > 180
        if reversing:
            leftDC = leftDC * -1
            rightDC = rightDC * -1

        return int(leftDC), int(rightDC)

    def setBearing(self, bearing, speed):
        if (bearing < 0 or bearing > 359) and bearing != -1:
            raise ValueError("Invalid bearing: {}".format(bearing))

        if speed < 0 or speed > 1:
            raise ValueError("Invalid speed: {}".format(speed))

        leftDC, rightDC = self.getTargetMotorDCs(bearing, speed)
        for leftMotor in self.leftMotors:
            leftMotor.setMotion(leftDC)

        for rightMotor in self.rightMotors:
            rightMotor.setMotion(rightDC)

class ServoController:

    def __init__(self, pwmPin):
        self.pwmPin = pwmPin
        self.neutral = 75000
        self.amplitude = 35000
        self.frequency = 50
        self.speed_per_sec = 30000
        self.resolution = 0.01
        self.stopping = False

        # 1 is forward, -1 is backward, 0 is stop
        self.direction = 0

        self.pi = pigpio.pi()

        self.timingLock = Condition()
        self.timingThread = Thread(daemon=True, target=self.timingLoop)
        self.timingThread.start()

    def forward(self):
        with self.timingLock:
            self.direction = 1
            self.timingLock.notify()

    def backward(self):
        with self.timingLock:
            self.direction = -1
            self.timingLock.notify()

    def lookStop(self):
        with self.timingLock:
            self.direction = 0
            self.timingLock.notify()

    def stop(self):
        with self.timingLock:
            print("Waiting for servo to stop...")
            self.stopping = True
            self.timingLock.notify()

        print("Joining the timing thread")
        self.timingThread.join()
        print("Servo thread stopped")

    def timingLoop(self):
        print("Servo starting...")

        # go neutral first
        self.pi.hardware_PWM(self.pwmPin, self.frequency, self.neutral)
        time.sleep(2)

        currentPosition = self.neutral
        lastChangeTime = -1

        while True:
            with self.timingLock:
                if not self.__shouldBeMoving(currentPosition):
                    print("Servo idling...")
                    self.timingLock.wait()
                    print("Servo woke up...")

                if self.stopping:
                    break

                if lastChangeTime == -1:
                    changeDelta = self.speed_per_sec * self.resolution
                else:
                    timeDelta = time.time() - lastChangeTime
                    changeDelta = self.speed_per_sec * timeDelta

                if self.direction == 1:
                    currentPosition = int(min(currentPosition + changeDelta, self.neutral + self.amplitude))
                elif self.direction == -1:
                    currentPosition = int(max(currentPosition - changeDelta, self.neutral - self.amplitude))

            # print("Pin {} frequency {} position {}".format(self.pwmPin, self.frequency, currentPosition))
            self.pi.hardware_PWM(self.pwmPin, self.frequency, currentPosition)
            time.sleep(self.resolution)

        print("Servo stopping...")
        self.pi.hardware_PWM(self.pwmPin, self.frequency, 0)
        self.pi.stop()

    def __shouldBeMoving(self, currentPosition):
        if self.direction == 0:
            return False
        elif self.direction == 1 and currentPosition >= self.neutral + self.amplitude:
            return False
        elif self.direction == -1 and currentPosition <= self.neutral - self.amplitude:
            return False

        return True





class Driver:

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

        print("Creating motor controller...")

        config = configparser.ConfigParser()
        config.read("rover.conf")

        leftMotorConfig = config["LEFTMOTOR"]
        rightMotorConfig = config["RIGHTMOTOR"]
        servoConfig = config["SERVO"]

        leftMotors = [Motor(int(leftMotorConfig["PWMPin"]),
                            int(leftMotorConfig["ForwardPin"]),
                            int(leftMotorConfig["ReversePin"]),
                            float(leftMotorConfig["Trim"]))]

        rightMotors = [Motor(int(rightMotorConfig["PWMPin"]),
                            int(rightMotorConfig["ForwardPin"]),
                            int(rightMotorConfig["ReversePin"]),
                            float(rightMotorConfig["Trim"]))]

        self.motorController = MotorController(leftMotors, rightMotors)
        self.servoController = ServoController(int(servoConfig["PWMPin_BCM"]))

    def setBearing(self, bearing, speed):
        self.motorController.setBearing(bearing, speed)

    def stop(self):
        self.motorController.setBearing(-1, 0)

    def lookUp(self):
        self.servoController.backward()

    def lookDown(self):
        self.servoController.forward()

    def lookStop(self):
        self.servoController.lookStop()

    def cleanup(self):
        GPIO.cleanup()
        self.servoController.stop()


