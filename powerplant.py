import pigpio

class PowerPlant:
    def __init__(self, config, gpio):
        self.gpio = gpio
        powerplantConfig = config["POWERPLANT"]
        self.inputPinVal = int(powerplantConfig["InputPin"])
        self.chargingPinVal = int(powerplantConfig["ChargingPin"])
        self.lowBatteryPinVal = int(powerplantConfig["LowBatteryPin"])

        self.gpio.set_mode(self.inputPinVal, pigpio.INPUT)
        self.gpio.set_pull_up_down(self.inputPinVal, pigpio.PUD_DOWN)

        self.gpio.set_mode(self.chargingPinVal, pigpio.INPUT)
        self.gpio.set_pull_up_down(self.chargingPinVal, pigpio.PUD_DOWN)

        self.gpio.set_mode(self.lowBatteryPinVal, pigpio.INPUT)
        self.gpio.set_pull_up_down(self.lowBatteryPinVal, pigpio.PUD_DOWN)

    def getBatteryInfo(self):
        hasInput = self.gpio.read(self.inputPinVal) == 1
        charging = self.gpio.read(self.chargingPinVal) == 1
        lowBattery = self.gpio.read(self.lowBatteryPinVal) == 1

        batteryStr = "OK" if not lowBattery else "Low"
        chargingString = "Charging" if hasInput and charging else "Charged" if hasInput and not charging else ""
        return [batteryStr, chargingString]