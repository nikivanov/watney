import alsaaudio
import pigpio


class Alsa:
    def __init__(self, pi, mutePin, janusMonitor):
        try:
            if len(alsaaudio.mixers()) > 0:
                self.mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
            else:
                self.mixer = None
        except alsaaudio.ALSAAudioError:
            self.mixer = None

        self.pi = pi
        self.mutePin = mutePin
        self.pi.set_mode(self.mutePin, pigpio.OUTPUT)
        self.mute()
        janusMonitor.addWatcher(lambda sessionPresent: self.handleSessionChange(sessionPresent))

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

    def handleSessionChange(self, sessionPresent):
        if sessionPresent:
            self.unmute()
        else:
            self.mute()

    def stop(self):
        self.mute()

    def mute(self):
        self.pi.write(self.mutePin, 0)

    def unmute(self):
        self.pi.write(self.mutePin, 1)

