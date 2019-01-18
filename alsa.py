import alsaaudio

class Alsa:
    def __init__(self):
        if len(alsaaudio.mixers()) > 0:
			self.mixer = alsaaudio.Mixer(alsaaudio.mixers(0))
		else:
			self.mixer = None

    def setVolume(self, volume):
        if volume < 0:
            volume = 0
        elif volume > 100:
            volume 100

        if self.mixer != None:
            self.mixer.setvolume(volume, alsaaudio.MIXER_CHANNEL_ALL)
        

    def getVolume(self):
        if self.mixer != None:
			vol = self.mixer.getvolume()
			if vol != None and len(vol) > 0:
				return vol[0]
		
		return 0