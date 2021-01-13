gst-launch-1.0 alsasrc device=plughw:0,0 ! audio/x-raw,format=S16LE,layout=interleaved,rate=48000,channels=1 ! volume volume=10 ! volume volume=3 ! opusenc ! oggmux ! filesink location=test.ogg
