gst-launch-1.0 \
rtpbin name=rtpbin latency=100 \
udpsrc port=50000 caps="application/x-rtp, media=audio, encoding-name=OPUS, clock-rate=48000" ! rtpbin.recv_rtp_sink_0 \
udpsrc port=50001 caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_0 \
rtpbin. ! rtpopusdepay ! queue ! opusdec ! audioresample ! audio/x-raw,format=S16LE,layout=interleaved,rate=16000,channels=1 ! webrtcechoprobe ! alsasink \
alsasrc device=plughw:0,0 buffer-time=20000 ! audio/x-raw,format=S16LE,layout=interleaved,rate=16000,channels=1 ! webrtcdsp noise-suppression-level=high echo-suppression-level=high ! volume volume=10 ! volume volume=3 ! \
queue ! opusenc ! rtpopuspay ! udpsink host=127.0.0.1 port=8005