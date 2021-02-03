import Adafruit_ADS1x15
from events import Events
import json
import numpy

class BatteryMonitor:
    def __init__(self, config):
        try:
            self.adc = Adafruit_ADS1x15.ADS1115(busnum=3)
        except:
            self.adc = None
            print('Unable to connect to the ADC')
        
        Events.getInstance().sessionStarted.append(lambda: self.onSessionStarted())
        Events.getInstance().sessionEnded.append(lambda: self.onSessionEnded())
        batteryMap = json.loads(config['BATTERY']['VoltageMap'])
        self.sortedKeys = sorted(map(lambda k: float(k), batteryMap.keys()))
        self.sortedValues = list(map(lambda k: batteryMap[str(k)], self.sortedKeys))

    def onSessionStarted(self):
        if self.adc:
            self.adc.start_adc(0, gain=2/3)

    def onSessionEnded(self):
        if self.adc:
            self.adc.stop_adc()

    def getVoltageAndPercentage(self):
        if self.adc:
            result  = self.adc.get_last_result()
            voltage = (result / 32767.0) * 6.144
            percentage = numpy.interp([voltage], self.sortedKeys, self.sortedValues)[0]
            return [voltage, percentage]
        else:
            return [0, 0]

