import os
import subprocess
from bluetoothctl import Bluetoothctl
from pathlib import Path
import time
import sys
import pigpio


class BLAudio():
    def __init__(self, pi, mutePin, deviceName, janusMonitor):
        super().__init__()
        self.mutePin = mutePin
        self.deviceName = deviceName
        self.pi = pi
        self.pi.set_mode(self.mutePin, pigpio.OUTPUT)
        self.mute()
        self.macaddress = None
        janusMonitor.addWatcher(lambda sessionPresent: self.handleSessionChange(sessionPresent))


    def waitForAudio(self):
        found = False
        print("Scanning for bluetooth devices")
        btctl = Bluetoothctl()
        btctl.get_paired_devices() # the first call always fails for some reason, but the second always succeeds
        pairedDevices = btctl.get_paired_devices()
        pairedDevice = next((filter(lambda d: d["name"].lower() == self.deviceName.lower(), pairedDevices)), None)
        if pairedDevice is not None:
            print("Device already paired!")
        else:
            print("Device not paired, scanning...")
            btctl.start_scan()
            addr, name = None, None
            while not found:
                for device in btctl.get_available_devices():
                    if device["name"].lower() == self.deviceName.lower():
                        print("Found matching device!")
                        found = True
                        addr = device["mac_address"]
                        name = device["name"]
                        btctl.out = btctl.get_output("scan off")
                        break

                time.sleep(2)

            print("Found {} {}".format(name, addr))
            home = str(Path.home())
            fullPath = os.path.join(home, ".asoundrc")
            print("Updating {} with bluetooth device values".format(fullPath))
            lines = [
                "defaults.bluealsa.interface \"hci0\"",
                "defaults.bluealsa.device \"{}\"".format(addr),
                "defaults.bluealsa.profile \"a2dp\"",
                "defaults.bluealsa.delay 10000"
            ]
            with open(fullPath, mode='w') as alsaConfig:
                alsaConfig.write('\n'.join(lines) + '\n')

            print("Restarting ALSA")
            subprocess.call("alsactl kill rescan", shell=True)

            print("Pairing...")
            if btctl.pair(addr):
                print("Paired successfully!")
            else:
                print("Paired unsuccessfully")
                sys.exit(1)

            pairedDevice = next((filter(lambda d: d["name"].lower() == self.deviceName.lower(), btctl.get_paired_devices())))

        print("Connecting to {} {}".format(pairedDevice["name"], pairedDevice["mac_address"]))
        print("Connecting...")
        if btctl.connect(pairedDevice["mac_address"]):
            print("Connected successfully!")
            self.macaddress = pairedDevice["mac_address"]
            time.sleep(4)  # the bluetootha deewice is connected ahsuccessfully
            self.unmute()
        else:
            print("Failed to connect!")

    def mute(self):
        self.pi.write(self.mutePin, 0)

    def unmute(self):
        self.pi.write(self.mutePin, 1)

    def handleSessionChange(self, sessionPresent):
        if sessionPresent:
            self.unmute()
        else:
            self.mute()

    def stop(self):
        self.mute()
        btctl = Bluetoothctl()
        btctl.disconnect(self.macaddress)
        time.sleep(4)
