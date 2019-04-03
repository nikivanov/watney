import configparser
import pigpio
import os
from motor import Motor
from motorcontroller import MotorController
from servocontroller import ServoController
from tts import TTSSpeaker
from heartbeat import Heartbeat
from alsa import Alsa
from externalrunner import ExternalRunner
from janusmonitor import JanusMonitor


class Driver:

    def __init__(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.pi = pigpio.pi()

        config = configparser.ConfigParser()
        config.read("rover.conf")

        self.janusMonitor = JanusMonitor()
        self.externalRunner = ExternalRunner(self.janusMonitor)

        audioConfig = config["AUDIO"]
        videoConfig = config["VIDEO"]
        driverConfig = config["DRIVER"]
        leftMotorConfig = config["LEFTMOTOR"]
        rightMotorConfig = config["RIGHTMOTOR"]
        servoConfig = config["SERVO"]

        ttsCommand = audioConfig["TTSCommand"]
        greeting = audioConfig["Greeting"]
        mutePin = int(audioConfig["MutePin"])

        self.alsa = Alsa(self.pi, mutePin, self.janusMonitor)

        print("Starting video GStreamer pipeline...")
        self.externalRunner.addExternalProcess(videoConfig["GStreamerStartCommand"], True, False, True)

        print("Starting audio GStreamer pipeline...")
        self.externalRunner.addExternalProcess(audioConfig["GStreamerStartCommand"], True, False, True)

        print("Starting Janus gateway...")
        self.externalRunner.addExternalProcess(videoConfig["JanusStartCommand"], True, False, False)

        print("Starting Audio Sink...")
        self.externalRunner.addExternalProcess(audioConfig["AudioSinkCommand"], True, True, True)

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

        self.servoController = ServoController(self.pi, int(servoConfig["PWMPin"]), readyEvent)

        self.tts = TTSSpeaker(ttsCommand)

        heartbeatInterval = float(driverConfig["MaxHeartbeatInvervalMS"])
        self.heartbeat = Heartbeat(heartbeatInterval, self.servoController, self.motorController, self.alsa)

        readyEvent.wait()

        if greeting:
            self.alsa.unmute()
            self.tts.addPhrase(greeting)
            self.alsa.mute()

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

    def cleanup(self):
        # external runner must be shutdown first to minimize the shutdown / restart race condition
        self.externalRunner.shutdown()
        self.alsa.stop()
        self.servoController.stop()
        self.tts.stop()
        self.heartbeat.stop()
        self.pi.stop()
