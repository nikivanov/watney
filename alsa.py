import alsaaudio
from events import Events
import pigpio


class Alsa:
    def __init__(self, gpio, config):
        audioConfig = config["AUDIO"]
        mutePin = int(audioConfig["MutePin"])
        self.isMuted = False
        self.gpio = gpio
        try:
            if len(alsaaudio.mixers()) > 0:
                self.mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
            else:
                self.mixer = None
        except alsaaudio.ALSAAudioError:
            self.mixer = None

        self.mutePin = mutePin
        self.gpio.set_mode(self.mutePin, pigpio.OUTPUT)
        
        self.mute()

        Events.getInstance().sessionStarted.append(lambda: self.onSessionStarted())
        Events.getInstance().sessionEnded.append(lambda: self.onSessionEnded())

    def setVolume(self, volume):
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume = 100

        if self.mixer is not None:
            self.mixer.setvolume(volume, alsaaudio.MIXER_CHANNEL_ALL)

    def getVolume(self):
        if self.mixer is not None:
            vol = self.mixer.getvolume()
            if vol is not None and len(vol) > 0:
                return vol[0]

        return 0

    def onSessionStarted(self):
        self.unmute()

    def onSessionEnded(self):
        self.mute()

    def stop(self):
        self.mute()

    def mute(self):
        self.gpio.write(self.mutePin, pigpio.LOW)
        self.isMuted = True

    def unmute(self):
        self.gpio.write(self.mutePin, pigpio.HIGH)
        self.isMuted = False
