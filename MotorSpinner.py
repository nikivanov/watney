import RPi.GPIO as GPIO
from time import sleep
import math
import pygame
from pygame.locals import *
import threading


class Motor(object):

    def __init__(self, pins, reverse):
        self.P1 = pins[0]
        self.P2 = pins[1]
        self.P3 = pins[2]
        self.P4 = pins[3]
        self.reverse = reverse

    def getCWSequence(self):
        if self.reverse:
            return [self.P1, self.P3, self.P4, self.P2, self.P3, self.P1, self.P2, self.P4]
        else:
            return [self.P3, self.P1, self.P4, self.P2, self.P1, self.P3, self.P2, self.P4]

    def getCCWSequence(self):
        if self.reverse:
            return [self.P3, self.P1, self.P4, self.P2, self.P1, self.P3, self.P2, self.P4]
        else:
            return [self.P1, self.P3, self.P4, self.P2, self.P3, self.P1, self.P2, self.P4]


class MotorSpinner(object):

    def __init__(self, motors):
        self.motors = motors
        self.deg_per_step = 5.625 / 64  # for half-step drive (mode 3)
        self.steps_per_rev = int(360 / self.deg_per_step)  # 4096
        self.step_angle = 0  # Assume the way it is pointing is zero degrees

        self.mmPerRev = math.pi * 65

        for motor in motors:
            GPIO.setup(motor.P1, GPIO.OUT)
            GPIO.output(motor.P1, 0)

            GPIO.setup(motor.P2, GPIO.OUT)
            GPIO.output(motor.P2, 0)

            GPIO.setup(motor.P3, GPIO.OUT)
            GPIO.output(motor.P3, 0)

            GPIO.setup(motor.P4, GPIO.OUT)
            GPIO.output(motor.P4, 0)

    def _set_rpm(self, rpm):
        """Set the turn speed in RPM."""
        self._rpm = rpm
        # T is the amount of time to stop between signals
        self._T = (60.0 / rpm) / self.steps_per_rev

    # This means you can set "rpm" as if it is an attribute and
    # behind the scenes it sets the _T attribute
    rpm = property(lambda self: self._rpm, _set_rpm)

    def __clear(self):
        for motor in self.motors:
            GPIO.output(motor.P1, 0)
            GPIO.output(motor.P2, 0)
            GPIO.output(motor.P3, 0)
            GPIO.output(motor.P4, 0)

    def rotate(self, angle, turning):
        """Take the shortest route to a particular angle (degrees)."""
        # Make sure there is a 1:1 mapping between angle and stepper angle
        absAngle = abs(angle)
        steps = int(absAngle / self.deg_per_step)

        if angle < 0:
            # steps -= self.steps_per_rev
            # print ("moving " + repr(steps) + " steps")
            self._move_acw_3(int(steps / 8), turning)
        else:
            # print ("moving " + repr(steps) + " steps")
            self._move_cw_3(int(steps / 8), turning)

    def _move_acw_3(self, big_steps, turning):
        self.__clear()
        for i in range(big_steps):
            for pinIx in range(0, 8):
                motor1 = self.motors[0]
                motor2 = self.motors[1]
                GPIO.output(motor1.getCCWSequence()[pinIx], pinIx % 2)
                if turning:
                    GPIO.output(motor2.getCWSequence()[pinIx], pinIx % 2)
                else:
                    GPIO.output(motor2.getCCWSequence()[pinIx], pinIx % 2)

                sleep(self._T)

    def _move_cw_3(self, big_steps, turning):
        self.__clear()
        for i in range(big_steps):
            for pinIx in range(0, 8):
                motor1 = self.motors[0]
                motor2 = self.motors[1]

                GPIO.output(motor1.getCWSequence()[pinIx], pinIx % 2)
                if turning:
                    GPIO.output(motor2.getCCWSequence()[pinIx], pinIx % 2)
                else:
                    GPIO.output(motor2.getCWSequence()[pinIx], pinIx % 2)

                sleep(self._T)



    def moveForward(self, distanceMM):
        revs = distanceMM / self.mmPerRev
        self.rotate(revs * 360, False)

    def moveBackwards(self, distanceMM):
        revs = distanceMM / self.mmPerRev
        self.rotate(revs * 360 * -1, False)

    def turnLeft(self, degree):
        self.rotate(degree * 2, True)

    def turnRight(self, degree):
        self.rotate(degree * -2, True)

    up = False
    down = False
    left = False
    right = False

    bigStepsPerKey = 10
    moveLock = threading.Lock()
    moveMonitor = threading.Condition(moveLock)

    def makeMove(self, p_up, p_down, p_left, p_right):
        with self.moveLock:
            self.up = p_up
            self.down = p_down
            self.left = p_left
            self.right = p_right

            if p_up or p_down or p_left or p_right:
                self.moveMonitor.wait()

    def spinnerThread(self):
        while True:
            with self.moveLock:
                if self.up:
                    self._move_cw_3(self.bigStepsPerKey, False)
                elif self.down:
                    self._move_acw_3(self.bigStepsPerKey, False)
                elif self.left:
                    self._move_cw_3(self.bigStepsPerKey, True)
                elif self.right:
                    self._move_acw_3(self.bigStepsPerKey, True)

                self.moveMonitor.notify()


    def startSpinnerThread(self):
        spinThread = threading.Thread(target=self.spinnerThread, daemon=True)
        spinThread.start()




if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)

    motor1 = Motor([8, 10, 12, 11], False)
    motor2 = Motor([36, 38, 40, 37], True)

    spinner = MotorSpinner([motor1, motor2])
    spinner.rpm = 20

    spinner.startSpinnerThread()

    pygame.init()
    screen = pygame.display.set_mode((100, 100))

    done = False
    up = False
    down = False
    left = False
    right = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    up = True
                elif event.key == pygame.K_DOWN:
                    down = True
                elif event.key == pygame.K_LEFT:
                    left = True
                elif event.key == pygame.K_RIGHT:
                    right = True
                elif event.key == pygame.K_q:
                    done = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    up = False
                elif event.key == pygame.K_DOWN:
                    down = False
                elif event.key == pygame.K_LEFT:
                    left = False
                elif event.key == pygame.K_RIGHT:
                    right = False

        spinner.makeMove(up, down, left, right)

    GPIO.cleanup()
