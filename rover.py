import configparser
import pigpio
from threading import Thread
import time
import os
import subprocess
import re
import sys
import shlex
from motor import Motor
from motorcontroller import MotorController
from servocontroller import ServoController


class Driver:

    def __init__(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.pi = pigpio.pi()

        config = configparser.ConfigParser()
        config.read("rover.conf")

        self.childProcesses = []

        videoConfig = config["VIDEO"]
        driverConfig = config["DRIVER"]
        leftMotorConfig = config["LEFTMOTOR"]
        rightMotorConfig = config["RIGHTMOTOR"]
        servoConfig = config["SERVO"]

        print("Starting GStreamer pipeline...")
        self.execAndMonitor(videoConfig["GStreamerStartCommand"])

        print("Starting Janus gateway...")
        self.execAndMonitor(videoConfig["JanusStartCommand"])

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

        heartbeatInterval = float(driverConfig["MaxHeartbeatInvervalMS"])
        self.ssidRegex = re.compile(r"ESSID:\"(.+?)\"")
        self.qualityRegex = re.compile(r"Link Quality=([^ ]+)")
        self.signalRegex = re.compile(r"Signal level=(.*? dBm)")
        self.lastHeartbeat = time.time()
        self.heartbeatThread = Thread(daemon=True, target=self.heartbeatLoop, args=[heartbeatInterval])
        self.heartbeatThread.start()

    shuttingDown = False
    lastHeartbeat = -1
    heartbeatStop = False
    lastHeartbeatData = {
                "SSID": "-",
                "Quality": "-",
                "Signal": "-"
            }

    def heartbeatLoop(self, maxInterval):
        print("Starting heartbeat thread...")
        while not self.shuttingDown:
            if (time.time() - self.lastHeartbeat) > maxInterval:
                if not self.heartbeatStop:
                    self.stop()
                    self.lookStop()
                    self.heartbeatStop = True
            else:
                self.heartbeatStop = False

            self.lastHeartbeatData = self.collectHeartbeatData()
            time.sleep(0.5)

    def collectHeartbeatData(self):
        try:
            wifiInfo = subprocess.check_output("iwconfig wlan0", shell=True).decode("utf-8")
            ssidMatch = self.ssidRegex.search(wifiInfo)
            ssid = ssidMatch.group(1) if ssidMatch else "-"

            qualityMatch = self.qualityRegex.search(wifiInfo)
            quality = qualityMatch.group(1) if qualityMatch else "-"

            signalMatch = self.signalRegex.search(wifiInfo)
            signal = signalMatch.group(1) if signalMatch else "-"

            return {
                "SSID": ssid,
                "Quality": quality,
                "Signal": signal
            }
        except Exception as ex:
            print(str(ex), file=sys.stderr)
            return {
                "SSID": "-",
                "Quality": "-",
                "Signal": "-"
            }

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

    def onHeartbeat(self):
        self.lastHeartbeat = time.time()
        return self.lastHeartbeatData

    def execAndMonitor(self, command):
        args = shlex.split(command)
        print("Starting: " + str(args))
        p = subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr, shell=True)
        self.childProcesses.append(p)

    def cleanup(self):
        self.servoController.stop()
        self.pi.stop()
        self.shuttingDown = True
        print("Waiting for heartbeat thread to stop...")
        self.heartbeatThread.join()
        print("Heartbeat thread stopped")
        for p in self.childProcesses:
            p.terminate()
