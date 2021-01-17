import re
import time
import asyncio
import sys
import psutil


class Heartbeat:
    def __init__(self, config, servoController, motorController, alsa, lightsController):
        driverConfig = config["DRIVER"]
        self.heartbeatInterval = float(driverConfig["MaxHeartbeatInvervalS"])

        self.servoController = servoController
        self.motorController = motorController
        self.alsa = alsa
        self.ssidRegex = re.compile(r"ESSID:\"(.+?)\"")
        self.qualityRegex = re.compile(r"Link Quality=([^ ]+)")
        self.signalRegex = re.compile(r"Signal level=(.*? dBm)")
        self.lastHeartbeat = time.time()
        self.task = None
        self.lightsController = lightsController

    lastHeartbeat = -1
    heartbeatStop = False
    lastHeartbeatData = {
        "SSID": "-",
        "Quality": "-",
        "Signal": "-",
        "Volume": 0,
        "CPU": "-",
        "Lights": False
    }

    def start(self):
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.heartbeatLoop())

    def stop(self):
        if self.task:
            self.task.cancel()

    async def heartbeatLoop(self):
        print("Heartbeat starting...")
        try:
            while True:
                if (time.time() - self.lastHeartbeat) > self.heartbeatInterval:
                    if not self.heartbeatStop:
                        self.motorController.setBearing("0", False)
                        await self.servoController.lookStop()
                        self.heartbeatStop = True
                else:
                    self.heartbeatStop = False

                self.lastHeartbeatData = await self.collectHeartbeatData()
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print("Heartbeat stopped")
        except Exception as e:
            print("Unexpected exception in heartbeat: " + str(e))

    async def collectHeartbeatData(self):
        try:
            proc = await asyncio.create_subprocess_shell(
                "iwconfig wlan0",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)

            stdout, stderr = await proc.communicate()

            wifiInfo = stdout.decode()
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
                "CPU": cpuIdle,
                "Lights": self.lightsController.lightsStatus
            }
        except Exception as ex:
            print(str(ex), file=sys.stderr)
            return {
                "SSID": "-",
                "Quality": "-",
                "Signal": "-",
                "Volume": 0,
                "CPU": "-",
                "Lights": False
            }

    def onHeartbeatReceived(self):
        self.lastHeartbeat = time.time()
        return self.lastHeartbeatData
