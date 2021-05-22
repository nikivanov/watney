import gi 
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
import threading
import concurrent
import time

PIPELINE = '''
rtpbin name=rtpbin latency=100 \
udpsrc port=50000 caps="application/x-rtp, media=audio, encoding-name=OPUS, clock-rate=48000" ! rtpbin.recv_rtp_sink_0 \
udpsrc port=50001 caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_0 \
rtpbin. ! rtpopusdepay ! queue ! opusdec ! audioresample ! audio/x-raw,format=S16LE,layout=interleaved,rate=16000,channels=1 ! webrtcechoprobe name=echoprobe ! alsasink \
alsasrc device=plughw:0,0 buffer-time=20000 ! audio/x-raw,format=S16LE,layout=interleaved,rate=16000,channels=1 ! webrtcdsp probe=echoprobe noise-suppression-level=high echo-suppression-level=high ! \
volume name=vol1 volume=10 ! volume name=vol2 volume=3 ! queue ! opusenc ! rtpopuspay ! udpsink host=127.0.0.1 port=8005
'''

class AudioManager:
    def __init__(self, config):
        self.pause = float(config["AUDIO"]["VolumeRestoreDelay"])

    def start(self):
        self.tokenSet = set()
        self.mutex = threading.Lock()
        self.delayedExecutor = concurrent.futures.ThreadPoolExecutor()
        
        audioManagerThread = threading.Thread(name='audioManagerLoop', target=self.__runLoop)
        audioManagerThread.setDaemon(True)
        audioManagerThread.start()

    def __runLoop(self):
        Gst.init(None)
        while True:
            print('Starting audio pipeline')
            self.pipeline = Gst.parse_launch(PIPELINE)
            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.on_message)
            self.pipeline.set_state(Gst.State.PLAYING)
            print('Audio pipeline started')
            GObject.threads_init()
            self.mainloop = GObject.MainLoop().new(None, False) 
            self.mainloop.run()

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            print('Audio pipeline EOS')
            self.destroyPipeline()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print('Audio pipeline error: {} {}'.format(err, debug))
            self.destroyPipeline()

    def destroyPipeline(self):
        self.pipeline.get_bus().remove_signal_watch()
        self.pipeline.set_state(Gst.State.NULL)
        self.mainloop.quit()

    def lowerVolume(self, token):
        with self.mutex:
            if len(self.tokenSet) == 0:
                self.pipeline.get_by_name('vol1').set_property('volume', 1)
                self.pipeline.get_by_name('vol2').set_property('volume', 1)
            self.tokenSet.add(token)


    def restoreVolume(self, token):
        with self.mutex:
            if token in self.tokenSet:
                self.tokenSet.remove(token)
                if len(self.tokenSet) == 0:
                    self.delayedExecutor.submit(self.__restoreVolume)

    def __restoreVolume(self):
        time.sleep(self.pause)
        with self.mutex:
            if len(self.tokenSet) == 0:
                self.pipeline.get_by_name('vol1').set_property('volume', 10)
                self.pipeline.get_by_name('vol2').set_property('volume', 3) 