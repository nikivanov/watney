import configparser
import pigpio
import os
import subprocess
import sys
import shlex
from motor import Motor
from motorcontroller import MotorController
from servocontroller import ServoController
from tts import TTSSpeaker
from heartbeat import Heartbeat
from alsa import Alsa
from threading import Event


class Driver:

    def __init__(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.pi = pigpio.pi()

        config = configparser.ConfigParser()
        config.read("rover.conf")

        self.childProcesses = []

        audioConfig = config["AUDIO"]
        videoConfig = config["VIDEO"]
        driverConfig = config["DRIVER"]
        leftMotorConfig = config["LEFTMOTOR"]
        rightMotorConfig = config["RIGHTMOTOR"]
        servoConfig = config["SERVO"]

        ttsCommand = audioConfig["TTSCommand"]
        greeting = audioConfig["Greeting"]

        print("Starting GStreamer pipeline...")
        self.executeCommand(videoConfig["GStreamerStartCommand"])

        print("Starting Janus gateway...")
        self.executeCommand(videoConfig["JanusStartCommand"])

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

        readyEvent = Event()

        self.servoController = ServoController(self.pi, int(servoConfig["PWMPin"]), readyEvent)

        self.tts = TTSSpeaker(ttsCommand)

        self.alsa = Alsa()

        heartbeatInterval = float(driverConfig["MaxHeartbeatInvervalMS"])
        self.heartbeat = Heartbeat(heartbeatInterval, self.servoController, self.motorController, self.alsa)

        readyEvent.wait()
        
        if greeting:
            self.tts.addPhrase(greeting)

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

    def sayTTS(self, ttsString):
        self.tts.addPhrase(ttsString)

    def setVolume(self, volume):
        self.alsa.setVolume(volume)

    def onHeartbeat(self):
        return self.heartbeat.onHeartbeatReceived()

    def executeCommand(self, command):
        args = shlex.split(command)
        p = subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr, shell=True)
        self.childProcesses.append(p)

    def cleanup(self):
        self.servoController.stop()
        self.tts.stop()
        self.heartbeat.stop()
        self.pi.stop()

        for p in self.childProcesses:
            p.terminate()
