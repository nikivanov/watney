gst-launch-1.0 alsasrc device=plughw:1,0 ! mulawenc ! rtppcmupay ! udpsink host=127.0.0.1 port=8005
