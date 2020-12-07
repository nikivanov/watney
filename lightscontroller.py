import pigpio
from events import Events

LED_COUNT = 8
class LightsController:
    def __init__(self, gpio, config):
        Events.getInstance().janusFirstConnect.append(lambda: self.onJanusConnected())
        self.gpio = gpio
        self.spi = gpio.spi_open(0, 2e6, 0xE0)

    def onJanusConnected(self):
        pass

    def lightsOn(self):
        self._setColor(255, 255, 255)

    def lightsOff(self):
        self._setColor(0, 0, 0)

    def stop(self):
        self.lightsOff()
        self.gpio.spi_close(self.spi)

    def _setColor(self, r, g, b):
        apa102_cmd=[0]*4 + [0xe1,0, 0, 0]*LED_COUNT + [255]*4
        for i in range(0, LED_COUNT):
            offset = (i*4) +4
            apa102_cmd[offset+1] = b
            apa102_cmd[offset+2] = g
            apa102_cmd[offset+3] = r
        self.gpio.spi_xfer(self.spi, apa102_cmd)