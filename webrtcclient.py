import ssl
import websockets
import asyncio
import json

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
gi.require_version('GstWebRTC', '1.0')
from gi.repository import GstWebRTC
gi.require_version('GstSdp', '1.0')
from gi.repository import GstSdp

# PIPELINE_DESC = '''
# webrtcbin name=sendrecv bundle-policy=max-bundle rpicamsrc preview=0 bitrate=1500000 inline-headers=true keyframe-interval=30 ! video/x-h264, width=1280, height=720, framerate=30/1, profile=baseline ! h264parse ! rtph264pay config-interval=1 pt=96 ! application/x-rtp,media=video,encoding-name=H264,payload=96 ! sendrecv. audiotestsrc is-live=true wave=red-noise ! audioconvert ! audioresample ! queue ! opusenc ! rtpopuspay ! queue ! application/x-rtp,media=audio,encoding-name=OPUS,payload=96 ! sendrecv.
# '''

PIPELINE_DESC = '''
webrtcbin name=sendrecv bundle-policy=max-bundle rpicamsrc preview=0 bitrate=1000000 inline-headers=true keyframe-interval=25 ! video/x-h264, width=1280, height=720, framerate=25/1, profile=baseline ! h264parse ! rtph264pay config-interval=1 pt=96 ! application/x-rtp,media=video,encoding-name=H264,payload=96 ! sendrecv. alsasrc device=plughw:1,0 ! audio/x-raw,format=S16LE,layout=interleaved,rate=8000,channels=1 ! mulawenc ! rtppcmupay ! application/x-rtp,media=audio,encoding-name=PCMU,payload=96 ! sendrecv.
'''

# VIDEO = 'rpicamsrc preview=0 bitrate=1500000 inline-headers=true keyframe-interval=30 ! video/x-h264, width=1280, ' \
#         'height=720, framerate=30/1, profile=baseline ! h264parse ! rtph264pay config-interval=1 pt=96 ! ' \
#         'application/x-rtp,media=video,encoding-name=H264,payload=96'
#
# AUDIO = 'alsasrc device=plughw:1,0 ! audio/x-raw,format=S16LE,layout=interleaved,rate=48000,channels=1 ! opusenc ! ' \
#         'rtpopuspay ! application/x-rtp,media=audio,encoding-name=OPUS,payload=96'
#
# PIPELINE = 'webrtcbin name=sendrecv bundle-policy=max-bundle {} ! sendrecv. {} ! sendrecv.'.format(VIDEO, AUDIO)


class WebRTCClient:
    def __init__(self):
        Gst.init(None)
        self.id_ = 0  # Watney is 0, browser is 1
        self.conn = None
        self.pipe = None
        self.webrtc = None
        self.peer_id = "1"
        self.server = 'wss://127.0.0.1:8443'
        self.espeak = None

    async def connect(self):
        sslctx = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        self.conn = await websockets.connect(self.server, ssl=sslctx)
        print("Connected, sending HELLO")
        await self.conn.send('HELLO %d' % self.id_)
        print("Sent HELLO")

    async def setup_call(self):
        print("Sending SESSION")
        await self.conn.send('SESSION {}'.format(self.peer_id))

    def send_sdp_offer(self, offer):
        text = offer.sdp.as_text()
        print('Sending offer:\n%s' % text)
        msg = json.dumps({'sdp': {'type': 'offer', 'sdp': text}})
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.conn.send(msg))

    def on_offer_created(self, promise, _, __):
        promise.wait()
        reply = promise.get_reply()
        offer = reply['offer']
        promise = Gst.Promise.new()
        self.webrtc.emit('set-local-description', offer, promise)
        promise.interrupt()
        self.send_sdp_offer(offer)

    def on_negotiation_needed(self, element):
        print("Negotiation started")
        promise = Gst.Promise.new_with_change_func(self.on_offer_created, element, None)
        element.emit('create-offer', None, promise)

    def send_ice_candidate_message(self, _, mlineindex, candidate):
        print("Sending ICE message")
        icemsg = json.dumps({'ice': {'candidate': candidate, 'sdpMLineIndex': mlineindex}})
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.conn.send(icemsg))

    def on_incoming_decodebin_stream(self, _, pad):
        if not pad.has_current_caps():
            print (pad, 'has no caps, ignoring')
            return

        caps = pad.get_current_caps()
        assert (len(caps))
        s = caps[0]
        name = s.get_name()
        if name.startswith('video'):
            sink = Gst.ElementFactory.make('fakesink')
            self.pipe.add(sink)
            self.pipe.sync_children_states()
            pad.link(sink.get_static_pad('sink'))
        elif name.startswith('audio'):
            sink = Gst.ElementFactory.make('fakesink')
            self.pipe.add(sink)
            self.pipe.sync_children_states()
            pad.link(sink.get_static_pad('sink'))
            # mixer = Gst.ElementFactory.make('audiomixer')
            # audioPad = mixer.get_request_pad("sink_%u")
            # ttsPad = mixer.get_request_pad("sink_%u")
            #
            # conv = Gst.ElementFactory.make('audioconvert')
            # resample = Gst.ElementFactory.make('audioresample')
            # sink = Gst.ElementFactory.make('alsasink')
            #
            # self.espeak = Gst.ElementFactory.make("espeak")
            #
            # self.pipe.add(mixer, conv, resample, sink, self.espeak)
            # self.pipe.sync_children_states()
            # pad.link(audioPad)
            # self.espeak.link(ttsPad)
            # mixer.link(conv)
            # conv.link(resample)
            # resample.link(sink)

    def on_incoming_stream(self, _, pad):
        print("Got an incoming stream!")
        if pad.direction != Gst.PadDirection.SRC:
            return

        decodebin = Gst.ElementFactory.make('decodebin')

        decodebin.connect('pad-added', self.on_incoming_decodebin_stream)
        self.pipe.add(decodebin)
        decodebin.sync_state_with_parent()
        self.webrtc.link(decodebin)

    def start_pipeline(self):
        print("Parsing pipeline")
        self.pipe = Gst.parse_launch(PIPELINE_DESC)
        print("Parsed pipeline")
        self.webrtc = self.pipe.get_by_name('sendrecv')
        print("Got webrtc, attaching handlers")
        self.webrtc.connect('on-negotiation-needed', self.on_negotiation_needed)
        self.webrtc.connect('on-ice-candidate', self.send_ice_candidate_message)
        self.webrtc.connect('pad-added', self.on_incoming_stream)
        print("Attached handlers, setting pipeline state")
        self.pipe.set_state(Gst.State.PLAYING)
        print("Pipeline is running")

    async def handle_sdp(self, message):
        assert self.webrtc
        msg = json.loads(message)
        if 'sdp' in msg:
            sdp = msg['sdp']
            assert(sdp['type'] == 'answer')
            sdp = sdp['sdp']
            print('Received answer:\n%s' % sdp)
            res, sdpmsg = GstSdp.SDPMessage.new()
            GstSdp.sdp_message_parse_buffer(bytes(sdp.encode()), sdpmsg)
            answer = GstWebRTC.WebRTCSessionDescription.new(GstWebRTC.WebRTCSDPType.ANSWER, sdpmsg)
            promise = Gst.Promise.new()
            self.webrtc.emit('set-remote-description', answer, promise)
            promise.interrupt()
        elif 'ice' in msg:
            ice = msg['ice']
            candidate = ice['candidate']
            sdpmlineindex = ice['sdpMLineIndex']
            self.webrtc.emit('add-ice-candidate', sdpmlineindex, candidate)

    async def start(self):
        print("Connecting to signaling")
        await self.connect()
        print("Connected to signaling")
        print("Entering message loop")
        assert self.conn
        async for message in self.conn:
            if message == 'HELLO':
                await self.setup_call()
            elif message == 'SESSION_OK':
                self.start_pipeline()
            elif message.startswith('ERROR'):
                print(message)
                return 1
            else:
                await self.handle_sdp(message)
        return 0
