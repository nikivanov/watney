Watney Rover
------------


<p align="center">
  <img width="49%" height="auto" src="images/main_photo.png?raw=true">
  <img width="49%" height="auto" src="images/main_render.png?raw=true">
  <img width="100%" height="auto" src="images/evolution_of_watney.png?raw=true">
</p>

<h1>
<a href="https://i.imgur.com/pWdW8e0.gifv" target="_blank">Demo Video</a>
</h1>

Watney is a low-cost Raspberry Pi-enabled rover made of readily available parts. It has a Python and a REST APIs.
Watney is all-wheel drive, with each side powered by a geared motor. Because of that, it turns like a tank by spinning
each side in opposite directions. It drives best on smooth surfaces, like hardwood, linoleum and tile. For carpeted
surfaces, Watney can do "soft turns", by spinning one side forward and the other alternating backwards and forwards.

The software part of Watney makes it a webcam on wheels. The camera feed is low-latency HD and rover 
control is accessible via a browser.

The HD camera feed is provided by [rpi-webrtc-streamer](https://github.com/kclyu/rpi-webrtc-streamer).

Upon startup, Watney will detect if it's connected to a Wi-Fi hotspot. If not, it will host its own hotspot "Watney4".
Once you connect to the hotspot, you can control it directly by going to http://192.168.4.1:5000, or connect it to a Wi-Fi
hotspot by going to http://192.168.4.1. For advanced Wi-Fi setup, you can ssh to 192.168.4.1 (default credentials pi / 
watney4) and edit wpa_supplicant.conf directly.

Wi-Fi configuration is provided by [Raspberry Pi Turnkey](https://github.com/schollz/raspberry-pi-turnkey) 
 



Components
------------


All of these components can be found on Amazon, Ebay, AliExpress, Banggood and others.

* **Raspberry Pi Zero W**
* **SD Card 4GB+**
* **Sainsmart wide-angle Raspberry Pi camera** ([Sainsmart](https://www.sainsmart.com/products/noir-wide-angle-fov160-5-megapixel-camera-module) | [Amazon](http://a.co/eiLew1B))
* **Pi Zero-compatible camera cable**
* **USB power bank that provides at least 1A** Bigger is better as long as it fits on the roof
* **2x Arduino geared DC motors** ([Amazon](http://a.co/7sPakWM) | [AliExpress](https://www.aliexpress.com/item/TT-Motor-Smart-Car-Robot-Gear-Motor-for-Arduino-Free-Shipping/32529098435.html))
* **L298N H-bridge controller** ([Amazon](https://www.amazon.com/s/field-keywords=l298n) | [AliExpress](https://www.aliexpress.com/item/Free-Shipping-New-Dual-H-Bridge-DC-Stepper-Motor-Drive-Controller-Board-Module-L298N-MOTOR-DRIVER/32769190826.html))
* **Tiny Micro Nano Servo** ([Amazon](https://www.amazon.com/s/field-keywords=tiny+micro+nano+servo) | [AliExpress](https://www.aliexpress.com/item/Tiny-Micro-Nano-Servo-3-7g-For-RC-Airplane-Helicopter-Drone-Boat-For-Arduino/32766035136.html))
* **Jumper wire 15cm or longer** ([Amazon](http://a.co/e25UqlS))
* **M3 screws 6mm - 20mm** ([Amazon](http://a.co/eMCbWCn))



Assembly
--------
![Wiring](images/assembly.jpg?raw=true)

1. Print out all of the parts found in the STLs folder (See printing instructions on [Thingiverse](https://www.thingiverse.com/thing:2810420))
2. Install the GPIO header on the Raspberry Pi. Set up Raspbian and get it connected to your WiFi network
3. M3 screws are a bit too big for Raspberry Pi mounting holes. Run a 1/8" drill bit through them, file them, or just put an M3 screw through them carefully to expand them a bit.
4. Attach the parts as shown in the picture. Motors should face leads out with about 130mm of wire coming out of them. Match [Raspberry Pi BOARD GPIO](images/pi-gpio.png) with the controller as follows:
   * 12V - Pin 2
   * Gnd - Pin 14
   * ENA - Pin 36
   * IN1 - Pin 38
   * IN2 - Pin 40
   * IN3 - Pin 11
   * IN4 - Pin 13
   * ENB - Pin 15
   
Servo:
   * Black - Pin 6
   * Red - Pin 4
   * White - Pin 32
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

At this point, you should be able to access and control Watney on your computer by going to http://[Your Watney IP]:5000. Click on the input field at the bottom of the page and control your rover with arrow keys. Press Shift to sprint. Some geared DC motors don't like going at low speeds, so if your rover has trouble turning gradually (as when you press Up and Right, for instance), edit your index.html and change the non-turbo speed from 0.5 to 0.7.

You should shut down the rover gracefully before unplugging it from the power supply by executing "sudo halt" via SSH and waiting about 10 seconds for Linux to shut down.


Configuration
-------------

Rover configuration can be found in rover.conf:
* If you want to use different GPIO pins, you can specify them here
* If you find a motor running in reverse (backwards when it's supposed to be rotating forward) simply swap ForwardPin and ReversePin
* If you find the rover veering off to a side when it's supposed to be going straight, set the trim value appropriately. See the configuration file for an explanation
