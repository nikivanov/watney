Watney Rover
------------

![Main Photo](images/main_photo.jpg?raw=true)

![Evolution of Watney](images/evolution_of_watney.png?raw=true)

<h1>
<a href="https://i.imgur.com/pWdW8e0.gifv" target="_blank">Demo Video</a>
</h1>

Watney is a low-cost Raspberry Pi-enabled rover made of readily available parts.
The majority of Watney's parts are 3D-printable.
It has a Python and a REST APIs.
Watney is all-wheel drive, with each wheel powered by a geared motor. Because of that, it turns like a tank by spinning
each side in opposite directions. It drives great indoors and can even manage short grass.

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
Ordering from China is significantly cheaper, but you'll have to wait about a month.

* **Raspberry Pi Zero W with GPIO header**
* **SD Card 4GB+**
* **Sainsmart wide-angle Raspberry Pi camera** ([Sainsmart](https://www.sainsmart.com/products/noir-wide-angle-fov160-5-megapixel-camera-module) | [Amazon](http://a.co/eiLew1B))
* **Pi Zero-compatible camera cable**
* **USB power bank with 2 USB ports** ([Monoprice](https://www.monoprice.com/product?p_id=15120) or similar) 
* **4x Arduino geared DC motors** ([Amazon](http://a.co/7sPakWM) | [AliExpress](https://www.aliexpress.com/item/TT-Motor-Smart-Car-Robot-Gear-Motor-for-Arduino-Free-Shipping/32529098435.html))
* **L298N H-bridge controller** ([Amazon](https://www.amazon.com/s/field-keywords=l298n) | [AliExpress](https://www.aliexpress.com/item/Free-Shipping-New-Dual-H-Bridge-DC-Stepper-Motor-Drive-Controller-Board-Module-L298N-MOTOR-DRIVER/32769190826.html))
* **Micro-USB breakout board** ([Amazon](http://a.co/d/dG7Ooki) | [AliExpress](https://www.aliexpress.com/item/5PCS-Breakout-Power-Supply-Module-Micro-USB-Interface-Power-Adapter-Board-USB-5V-Breakout-Module/32870381190.html))
* **Tiny Micro Nano Servo** ([Amazon](https://www.amazon.com/s/field-keywords=tiny+micro+nano+servo) | [AliExpress](https://www.aliexpress.com/item/Tiny-Micro-Nano-Servo-3-7g-For-RC-Airplane-Helicopter-Drone-Boat-For-Arduino/32766035136.html))
* **Jumper wire 20cm** ([Amazon](http://a.co/d/004c3N0))
* **M3 screws 6mm - 20mm** ([Amazon](http://a.co/eMCbWCn))



Assembly
--------
![Wiring](images/assembly_new.jpg?raw=true)

1. Print all parts except the tires in PETG. Print the tires in TPU.
    * 1x bottom.stl - print with a brim of about 15 lines to prevent edge lift
    * 1x camera body.stl 
    * 1x camera bucket.stl - print with supports
    * 1x camera cover.stl
    * 1x cover.stl - supports are needed for SD card opening. Add a brim to prevent edge lift
    * 4x motor holder.stl
    * 4x tire.stl - print in TPU. If you don't have TPU, use rubber bands
    * 2x left wheel.stl
    * 2x right wheel.stl
1. Solder 15cm of wire to motor terminals.
Solder each pair of leads together **in parallel** (left to left, right to right),
so you have 2 pairs of motors, each connected in parallel.
Make sure you don't cross them up or they'll spin in different directions.
1. Secure each pair of motors to the sides using 4 motor holders and 6mm M3 screws. I found it easier to put the screws in for a few millimeters to prime the mounting holes.
1. Connect each pair of leads to motor controller outputs.
Polarity here doesn't matter much because we'll be able to set it in the config later.
1. M3 screws are a bit too big for Raspberry Pi mounting holes. Run a 1/8" drill bit through them, file them, or just 
put an M3 screw through them carefully to expand them a bit. Attach the camera cable and the Micro-USB cable to the Raspberry Pi.
Secure the Pi to the cover using 6mm screws.
1. Secure the Micro USB breakout board to the cover with 6mm M3 screws. Connect another Micro USB cable to the port.
1. Connect the motor controller to the breakout board and Raspberry Pi using [Pi GPIO BOARD pins](images/pi-gpio.png?raw=true) as follows:
   * 12V - Breakout board VCC Pin (**NOT** the 5V)
   * Gnd - Breakout board Gnd Pin
   * ENA - Pin 36
   * IN1 - Pin 38
   * IN2 - Pin 40
   * IN3 - Pin 11
   * IN4 - Pin 13
   * ENB - Pin 15
1. Attach the servo to the cover using one of the servo's longest screws and a precision screwdriver.
1. Unfortunately, servo's 3 pin plug can't be plugged into the Raspberry Pi directly, so use Male-Female jumper wire
to hook up the servo as follows. I recommend coiling the wires and putting a heatshrink on them to keep everything neat.
    * Black - Pin 6
    * Red - Pin 4
    * White - Pin 32
1. Download the latest Watney release image and burn it onto the SD card. The latest image can be found in [Releases](https://github.com/nikivanov/watney/releases/latest). 
1. Connect your Pi to the power bank - you can leave the motors unplugged for now. The servo should move to the neutral position when it's booted up. Power down
the Pi.
1. Attach the servo arm to the camera body using the smaller screw from the servo set.
1. Attach the camera body to the servo in a vertical position. Remember - the servo will always start in this position upon bootup.
Be careful not to move the servo manually beyond its limits or apply too much pressure.
1. Power on the Pi again, go to http://[IP]:5000 (or http://watney4.local:5000 if you're running mDNS) and verify
servo's range of motion by using A and Z keys. Power the Pi down.
1. Tilt the camera body a bit forward and put the camera bucket over it. Secure the bucket to the cover with a 6mm screw.
1. Use a 6mm M3 screw to secure the other side of the camera body. Don't overtighten.
1. Thread the camera cable through the bucket into the camera body. Tilt the body forward, attach the camera to the cable
and insert the camera into the body. Snap the cover on by snapping in the top part, then tilting the camera the other way
and snapping the bottom part.
1. Plug the Micro USB breakout board into the USB port with a higher amperage. Plug the Pi into the other port.
Let it power on and verify that the camera works, and all wheels are turning. Wheels on each side should spin in the same
direction at all times - if not, you switched the polarity of the leads.
1. Attach the motor controller to the bottom using 6mm screws.
1. Snap the cover onto the body. Use a 16mm screw to secure it in the back and a 6mm screw to secure the bucket to the bottom in the front.
Keep the cover on the camera lens so you don't accidentally scratch it.
1. Put tires on the wheels and attach the wheels.
1. Attach your power bank to the top of the cover using double-sided tape, hot glue etc.
1. You're done! Your Watney should be accessible at http://[IP]:5000 or, if you're running mDNS / bonjour, 
at http://watney4.local:5000


Configuration
-------------

Default credentials for Watney are pi / watney4. Watney's mDNS name is watney4.local.

Rover configuration can be found in ~/watney/rover.conf:
* If you want to use different GPIO pins, you can specify them here
* If you find motors on either side running in reverse (backwards when it's supposed to be rotating forward) simply swap ForwardPin 
and ReversePin
* You can also modify video stream properties by editing /opt/rws/etc/media_config.conf
* Restart your Watney for configuration changes to take effect

