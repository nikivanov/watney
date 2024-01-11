gst-launch-1.0 rtpbin name=rtpbin \
udpsrc port=50002 caps="application/x-rtp" ! rtpbin.recv_rtp_sink_0 \
udpsrc port=50003 caps="application/x-rtcp" ! rtpbin.recv_rtcp_sink_0 \
rtpbin. ! rtph264depay ! openh264dec ! glimagesink
