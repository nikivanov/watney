import pigpio
from apa102_pi.driver import apa102
from events import Events

LED_COUNT = 8
class LightsController:
    def __init__(self, gpio, config):
        Events.getInstance().janusFirstConnect.append(lambda: self.onJanusConnected())
        self.gpio = gpio
        self.lights = apa102.APA102(num_led=8, order='rgb')
        self.lights.set_global_brightness(31)
        self.lightsStatus = False

    def onJanusConnected(self):
        pass

    def lightsOn(self):
        for ix in range(0, LED_COUNT):
            self.lights.set_pixel_rgb(ix, 0xFFFFFF)
        self.lights.show()
        self.lightsStatus = True

    def lightsOff(self):
        self.lights.clear_strip()
        self.lightsStatus = False

    def stop(self):
        self.lightsOff()
        self.lights.cleanup()
        self.lightsStatus = False