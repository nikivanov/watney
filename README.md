Watney Rover
------------


<p align="center">
  <img width="32%" height="auto" src="images/watney.png?raw=true">
  <img width="32%" height="auto" src="images/watney-nocover.png?raw=true">
  <img width="32%" height="auto" src="images/watney-photo.jpg?raw=true">
  <img width="96%" height="auto" src="images/watneys.jpg?raw=true">
</p>


[Video](https://i.imgur.com/vydmPej.gifv)


Watney is a low-cost Raspberry Pi-enabled rover made of readily available parts. At the heart of it is
Raspberry Pi Zero W powered by a small phone battery bank. Two motors and a controller
provide direct drive to rear wheels and an RPi camera is mounted in the front.
Very little to no soldering required. The driving library is written in Python.


Besides the components listed above, some breadboard jumper wires and M3
screws, the rest of the components are 3D-printable.

The software part of Watney provides webcam-on-wheels functionality. The camera feed is low-latency HD and you control the rover from your browser. The HD camera feed is provided using the excellent [rpi-webrtc-streamer](https://github.com/kclyu/rpi-webrtc-streamer).


Work in Progress
----------------


Watney is a work in progress. Please report any issues you're having!

* Software installation can be streamlined
* Different camera housings for different type cameras
* Tires could be improved for more grip


Components
------------


All of these components can be found on Amazon, Ebay, AliExpress, Banggood and others.

* **Raspberry Pi Zero W**
If you live near a MicroCenter in the US, you could get one of these for $5. You also obviously need an SD card.
* **Raspberry Pi Camera with Zero-compatible cable**
I used a Raspberry Pi Camera v2, but you can get a cheap camera on ebay for about $9 if you search for "raspberry pi zero camera". You can also use the [fish-eye version](https://www.ebay.com/sch/i.html?_nkw=raspberry+pi+fisheye) to get a better field of view or the [IR version](https://www.ebay.com/sch/i.html?_nkw=raspberry+pi+night+vision) to have night vision.
* **USB power bank that provides at least 1A**
Bigger is better as long as it fits on the roof
* **2x Arduino geared DC motors** ([Amazon](http://a.co/7sPakWM) | [AliExpress](https://www.aliexpress.com/item/TT-Motor-Smart-Car-Robot-Gear-Motor-for-Arduino-Free-Shipping/32529098435.html))
* **L298N H-bridge controller** ([Amazon](http://a.co/1fvKKte) | [AliExpress](https://www.aliexpress.com/item/Free-Shipping-New-Dual-H-Bridge-DC-Stepper-Motor-Drive-Controller-Board-Module-L298N-MOTOR-DRIVER/32769190826.html))
* **Jumper wire 10cm or longer** ([Amazon](http://a.co/e25UqlS) or any other set of 10mm jumper wires)
* **M3 screws** ([Amazon](http://a.co/bRE14nB) or any other M3 set)

The major components (minus wire and screws) can be bought for around $40 depending on where you live.


Assembly
--------
![Wiring](images/Wiring.jpg?raw=true)

1. Print out all of the parts found in the STLs folder (See printing instructions on Thingiverse)
2. Install the GPIO header on the Raspberry Pi. Set up Raspbian and get it connected to your WiFi network
3. M3 screws are a bit too big for Raspberry Pi mounting holes. Run a 1/8" drill bit through them, file them, or just put an M3 screw through them carefully to expand them a bit.
4. Attach the parts as shown in the picture. Motors should face leads out with about 130mm of wire coming out of them. Match [Raspberry Pi BOARD GPIO](images/pi-gpio.png) with the controller as follows:
  * 12V - Pin 4
  * Gnd - Pin 6
  * ENA - Pin 16
  * IN1 - Pin 18
  * IN2 - Pin 22
  * IN3 - Pin 11
  * IN4 - Pin 13
  * ENB - Pin 15
5. Route the USB cable so it matches the notch on the cover, close the cover and secure it with a screw
6. Attach the caster mount using screws on the left and right. Attach the caster articulator and secure it with the cap. Put a screw through the center of the cap. Secure the caster wheel with a screw and a nut - use superglue or thread locker to make sure the nut stays in place without overtightening
7. Attach the camera mount, arm and the housing
8. Attach the wheels
9. Affix the battery pack to the roof using hotglue, double-side tape or something of that sort. Make sure the USB cable is long enough to reach the port


Software
--------

1. Clone the repo or download the repo zip and unpack it into the home directory of your Watney. SSH into Watney.
2. Install RWS: sudo dpkg -i rws_0.72.0_RaspiZeroW_armhf.deb
3. Modify media_config.conf if needed, though the default settings should be sufficient
4. Copy media_config.conf: sudo cp media_config.conf /opt/rws/etc/
5. Restart RWS to pick up the changes:
   * sudo systemctl stop rws
   * sudo systemctl start rws
6. Make sure Python 3 PIP is installed: sudo apt-get install python3-pip
7. Make sure Python 3 Rpi GPIO is installed: sudo apt-get install python3-rpi.gpio
8. Install Flask: pip3 install flask
9. Run Watney web server: python3 server.py

At this point, you should be able to access and control Watney on your computer by going to http://[Your Watney IP]:5000
