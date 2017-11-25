import atexit
import json
import time
from threading import Thread, Barrier
from time import sleep
import io
import base64
import RPi.GPIO as GPIO
import picamera
import pika

host = "172.18.22.21"
vhost = "/"
port = 5672
username = "admin"
password = "admin"
exchange = "watney"
bearing_topic = "bearing"
vision_topic = "vision"

class Motor:

    def __init__(self, pins, reverse, syncBarrier, timeRes, rpms, steeringCorrectionFactor):
        self.pins = pins
        self.reverse = reverse

        self.__setSequence()

        self.maxRPM = rpms
        self.__set_rpm(self.maxRPM)
        self.syncBarrier = syncBarrier
        self.bearing = -1
        self.timeRes = timeRes
        self.steeringCorrectionFactor = steeringCorrectionFactor

        self.__initMotor()

    def __setSequence(self):
        # seq = [[1, 0, 0, 0],
        #        [1, 1, 0, 0],
        #        [0, 1, 0, 0],
        #        [0, 1, 1, 0],
        #        [0, 0, 1, 0],
        #        [0, 0, 1, 1],
        #        [0, 0, 0, 1],
        #        [1, 0, 0, 1]]
        # degreePerStep = 5.625

        seq = [[0, 0, 1, 1],
               [1, 0, 0, 1],
               [1, 1, 0, 0],
               [0, 1, 1, 0]]
        degreePerStep = 11.25

        gearRatio = 1/64
        realDegreePerStep = degreePerStep * gearRatio
        self.steps_per_rev = int(360 / realDegreePerStep)

        if self.reverse:
            seq.reverse()

        self.sequence = seq

        return seq

    def __set_rpm(self, rpm):
        """Set the turn speed in RPM."""
        self._rpm = rpm
        if rpm > 0:
            # T is the amount of time to stop between signals
            self._T = (60.0 / rpm) / self.steps_per_rev
        else:
            self._T = -1

    def __initMotor(self):
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        self.__clear()

    def __clear(self):
        for pin in self.pins:
            GPIO.output(pin, 0)

    def setBearing(self, bearing):
        self.bearing = bearing

    def doDrive(self):
        print("Starting motor...")
        while True:
            if self.bearing == -1:
                self.__clear()
                sleep(self.timeRes)
                #self.syncBarrier.wait()

            else:
                if self.bearing > 90:
                    if self.reverse:
                        self.__set_rpm((float(180 - self.bearing) / 90) * self.steeringCorrectionFactor * self.maxRPM)
                    else:
                        self.__set_rpm(self.maxRPM)
                else:
                    if self.reverse:
                        self.__set_rpm(self.maxRPM)
                    else:
                        self.__set_rpm((float(self.bearing) / 90) * self.steeringCorrectionFactor * self.maxRPM)

                if self._rpm == 0:
                    self.bearing = -1
                else:
                    startTime = time.time()
                    while (time.time() - startTime) < self.timeRes:
                        for step in self.sequence:
                            for pinIx in range(0, 4):
                                GPIO.output(self.pins[pinIx], step[pinIx] % 2)

                            sleep(self._T)

                    #self.syncBarrier.wait()


class Driver:

    barrier = Barrier(2)
    timeResUnit = 0.2
    rpms = 10
    steeringCorrectionFactor = 1

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        print("Creating motors...")
        self.motor1 = Motor([8, 10, 12, 11], False, self.barrier, self.timeResUnit, self.rpms, self.steeringCorrectionFactor)
        self.motor2 = Motor([36, 38, 40, 37], True, self.barrier, self.timeResUnit, self.rpms, self.steeringCorrectionFactor)
        self.__startDriverThreads()

    def __startDriverThreads(self):
        print("Starting motor threads...")
        self.motor1Thread = Thread(target=self.motor1.doDrive, daemon=True)
        self.motor2Thread = Thread(target=self.motor2.doDrive, daemon=True)
        self.motor1Thread.start()
        self.motor2Thread.start()

    def setBearing(self, bearing):
        if bearing < 0 or bearing > 180:
            raise ValueError("Invalid bearing: " + bearing)

        self.motor1.setBearing(bearing)
        self.motor2.setBearing(bearing)

    def stop(self):
        self.motor1.setBearing(-1)
        self.motor2.setBearing(-1)


def onExit():
    print("Cleaning up and exiting...")
    GPIO.cleanup()


def onBearingReceived(channel, method, properties, body):
    messageStr = body.decode("utf-8")
    message = json.loads(messageStr)
    newBearing = int(message["bearing"])
    print("New Bearing: " + str(newBearing))
    if newBearing == -1:
        driver.stop()
    else:
        driver.setBearing(newBearing)

def cameraThread():
    print("Starting camera thread...")
    visionConnection = pika.BlockingConnection(parameters=connectionParameters)
    visionChannel = visionConnection.channel()
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)
    camera.hflip = True
    camera.vflip = True
    camera.shutter_speed = 15000
    camera.awb_mode = 'fluorescent'
    camera.exposure_mode = 'off'
    while True:
        stream = io.BytesIO()
        camera.capture(stream, 'png')
        picBytes = stream.getvalue()
        picB64String = base64.b64encode(picBytes).decode("utf-8")
        message = {
            "img": picB64String
        }
        messageStr = json.dumps(message)
        visionChannel.basic_publish(exchange=exchange, routing_key=vision_topic, body=messageStr)


if __name__ == "__main__":
    atexit.register(onExit)
    print("Creating driver...")
    driver = Driver()

    credentials = pika.PlainCredentials(username, password)
    connectionParameters = pika.ConnectionParameters(host, port, vhost, credentials)

    camera_thread = Thread(target=cameraThread, daemon=True)
    camera_thread.start()

    input("Watney is ready. Press Enter to start...")
    connection = pika.BlockingConnection(parameters=connectionParameters)
    bearingChannel = connection.channel()
    queue = bearingChannel.queue_declare(exclusive=True)
    bearingChannel.queue_bind(exchange=exchange, queue=queue.method.queue, routing_key=bearing_topic)
    bearingChannel.basic_consume(onBearingReceived, no_ack=True, queue=queue.method.queue)
    bearingChannel.start_consuming()






