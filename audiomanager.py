import gi 
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

PIPELINE = '''
rtpbin name=rtpbin latency=100 \
udpsrc port=50000 caps="application/x-rtp, media=audio, encoding-name=OPUS, clock-rate=48000" ! rtpbin.recv_rtp_sink_0 \
udpsrc port=50001 caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_0 \
rtpbin. ! rtpopusdepay ! queue ! opusdec ! audioresample ! audio/x-raw,format=S16LE,layout=interleaved,rate=16000,channels=1 ! webrtcechoprobe ! alsasink \
alsasrc device=plughw:0,0 buffer-time=20000 ! audio/x-raw,format=S16LE,layout=interleaved,rate=16000,channels=1 ! webrtcdsp noise-suppression-level=high echo-suppression-level=high ! volume name=vol1 volume=10 ! volume name=vol2 volume=3 ! \
queue ! opusenc ! rtpopuspay ! udpsink host=127.0.0.1 port=8005
'''

class AudioManager:
    def runLoop(self):
        Gst.init(None)
        print('Starting audio pipeline')
        self.pipeline = Gst.parse_launch(PIPELINE)
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        self.pipeline.set_state(Gst.State.PLAYING)
        print('Audio pipeline started')
        GObject.threads_init()
        mainloop = GObject.MainLoop().new(None, False) 
        mainloop.run()

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)
            print('Audio pipeline EOS')
        elif t == Gst.MessageType.ERROR:
            self.pipeline.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print('Audio pipeline error {} {}'.format(err, debug))

    def lowerVolume(self):
        self.pipeline.get_by_name('vol1').set_property('volume', 1)
        self.pipeline.get_by_name('vol2').set_property('volume', 1)

    def restoreVolume(self):
        self.pipeline.get_by_name('vol1').set_property('volume', 10)
        self.pipeline.get_by_name('vol2').set_property('volume', 3)