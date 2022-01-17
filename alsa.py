import alsaaudio
import json

class Alsa:
    def __init__(self, gpio, config):
        self.gpio = gpio
        try:
            if len(alsaaudio.mixers()) > 0:
                self.mixer = alsaaudio.Mixer(alsaaudio.mixers()[0])
            else:
                self.mixer = None
        except alsaaudio.ALSAAudioError:
            self.mixer = None

        volumeSteps = json.loads(config['AUDIO']['VolumeSteps'])
        self.volumeMap = dict(map(lambda item: (int(item[0]), item[1]), volumeSteps.items()))
        self.reverseVolumeMap = dict(map(lambda item: (item[1], int(item[0])), volumeSteps.items()))

    def setVolume(self, volume):
        if volume < 0:
            volume = 0
        elif volume > 5:
            volume = 5

        if self.mixer is not None:
            volumeValue = self.volumeMap.get(volume)
            if volumeValue > 100:
                volumeValue = 100
            elif volumeValue < 0:
                volumeValue = 0
            self.mixer.setvolume(volumeValue, alsaaudio.MIXER_CHANNEL_ALL)

    def getVolume(self):
        if self.mixer is not None:
            vol = self.mixer.getvolume()
            if vol is not None and len(vol) > 0:
                actualValue = vol[0]
                sliderValue = self.reverseVolumeMap.get(actualValue)
                if not sliderValue:
                    sliderValue = 0
                return sliderValue

        return 0