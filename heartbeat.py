import re
import time
from threading import Thread
import subprocess
import sys
import psutil


class Heartbeat:
    def __init__(self, heartbeatInterval, servoController, motorController, alsa):
        self.servoController = servoController
        self.motorController = motorController
        self.alsa = alsa
        self.ssidRegex = re.compile(r"ESSID:\"(.+?)\"")
        self.qualityRegex = re.compile(r"Link Quality=([^ ]+)")
        self.signalRegex = re.compile(r"Signal level=(.*? dBm)")
        self.lastHeartbeat = time.time()
        self.heartbeatThread = Thread(
            daemon=True, target=self.heartbeatLoop, args=[heartbeatInterval])
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
                    self.motorController.setBearing(-1)
                    self.servoController.lookStop()
                    self.heartbeatStop = True
            else:
                self.heartbeatStop = False

            self.lastHeartbeatData = self.collectHeartbeatData()
            time.sleep(0.5)
        print("Stopping heartbeat thread...")

    def collectHeartbeatData(self):
        try:
            wifiInfo = subprocess.check_output(
                "iwconfig wlan0", shell=True).decode("utf-8")
            ssidMatch = self.ssidRegex.search(wifiInfo)
            ssid = ssidMatch.group(1) if ssidMatch else "-"

            qualityMatch = self.qualityRegex.search(wifiInfo)
            quality = qualityMatch.group(1) if qualityMatch else "-"

            signalMatch = self.signalRegex.search(wifiInfo)
            signal = signalMatch.group(1) if signalMatch else "-"

            volume = int(self.alsa.getVolume())

            cpuIdle = psutil.cpu_percent()

            return {
                "SSID": ssid,
                "Quality": quality,
                "Signal": signal,
                "Volume": volume,
                "CPU": cpuIdle
            }
        except Exception as ex:
            print(str(ex), file=sys.stderr)
            return {
                "SSID": "-",
                "Quality": "-",
                "Signal": "-",
                "Volume": 0
            }

    def onHeartbeatReceived(self):
        self.lastHeartbeat = time.time()
        return self.lastHeartbeatData

    def stop(self):
        self.shuttingDown = True
        self.heartbeatThread.join()
