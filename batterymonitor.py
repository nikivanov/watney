import Adafruit_ADS1x15
from events import Events

class BatteryMonitor:
    def __init__(self):
        self.adc = Adafruit_ADS1x15.ADS1115(busnum=3)
        Events.getInstance().sessionStarted.append(lambda: self.onSessionStarted())
        Events.getInstance().sessionEnded.append(lambda: self.onSessionEnded())

    def onSessionStarted(self):
        self.adc.start_adc(0, gain=2/3)

    def onSessionEnded(self):
        self.adc.stop_adc()

    def getVoltage(self):
        result  = self.adc.get_last_result()
        return (result / 32767.0) * 6.144
