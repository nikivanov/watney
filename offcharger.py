import concurrent
from events import Events
import time


class OffCharger:
    def __init__(self, config, tts, motorController):
        enabled = bool(config["OFFCHARGER"]["Enabled"])
        self.gracePeriod = int(config["OFFCHARGER"]["GracePeriod"])
        self.initialDelay = int(config["OFFCHARGER"]["InitialDelay"])
        self.tts = tts
        self.motorController = motorController
        if enabled:
            print("Starting Off Charger Monitoring...")
            Events.getInstance().motionOn.append(lambda: self.onMotion())
            Events.getInstance().motionOff.append(lambda: self.onMotion())
            Events.getInstance().offCharger.append(lambda: self.onOffCharger())
            Events.getInstance().onCharger.append(lambda: self.onOnCharger())
            self.lastMotion = time.time()
            self.currentChargingState = False
            self.delayedExecutor = concurrent.futures.ThreadPoolExecutor()
        

    def onMotion(self):
        self.lastMotion = time.time()
    
    def onOffCharger(self):
        self.currentChargingState = False
        if (time.time() - self.lastMotion > self.gracePeriod):
            self.delayedExecutor.submit(self.__doOffCharger)

    def onOnCharger(self):
        self.currentChargingState = True

    def __doOffCharger(self):
        time.sleep(self.initialDelay)
        if not self.currentChargingState:
            print("Off Charger detected")
            self.tts.sayText("Off Charger")
            time.sleep(2)
            self.motorController.setBearing("n", False)
            time.sleep(1)
            self.motorController.setBearing("0", False)


        