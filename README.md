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

Watney is a low-cost Raspberry Pi-enabled rover made of readily available parts.
The majority of Watney's parts are 3D-printable.
It has a Python and a REST APIs.
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

* **Raspberry Pi Zero W with GPIO header**
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

1. Print all parts except the tires in PETG. Print tires in TPU.
    * 1x bottom.stl - print with a brim of about 15 lines to prevent edge lift
    * 1x camera body.stl 
    * 1x camera bucket.stl - print with supports
    * 1x camera cover.stl
    * 1x cover.stl - supports are only needed for the camera bucket opening. Add a brim to prevent edge lift.
    * 2x drive gear.stl
    * 1x motor housing.stl
    * 1x servo pillar.stl
    * 4x spacer.stl
    * 1x swivel pillar.stl
    * 4x tire.stl - print in TPU. If you don't have TPU, use rubber bands
    * 4x transfer gear.stl
    * 4x wheel.stl
    * 4x wheel gear.stl
2. Put tires over the wheels.
3. Match wheels with wheel gears. They should snap together without too much force. Snap a wheel gear and a wheel 
together through the hole in the body, put a spacer between the gear and the column and put a 20mm screw. Hold the screw
with an allen wrench while turning the wheel to drive the screw in. Don't overtighten. The wheel should rotate freely
and the screw cap should be flush with the column, or just stick out a tiny bit. Repeat for the other 3 wheels.
4. Install transfer gears next to the wheel gears, with spacers facing the columns, using 16mm screws.
5. Put the motors into the housing with leads facing outwards. Run the wires through the holes in the housing. Secure
the housing to the bottom with 6mm screws. The wires should be about 130mm long.
6. M3 screws are a bit too big for Raspberry Pi mounting holes. Run a 1/8" drill bit through them, file them, or just 
put an M3 screw through them carefully to expand them a bit. Attach the camera cable to the Raspberry Pi and secure it 
to the cover using 6mm screws. Attach the Micro-USB cable from the power bank to the Raspberry Pi.
7. Connect motor wires to the outputs of the motor controller. Connect the controller to the Raspberry Pi as follows:
   * 12V - Pin 2
   * Gnd - Pin 14
   * ENA - Pin 36
   * IN1 - Pin 38
   * IN2 - Pin 40
   * IN3 - Pin 11
   * IN4 - Pin 13
   * ENB - Pin 15
8. Attach the motor controller to the bottom using 6mm screws.
9. Secure the camera bucket to the cover using 6mm screws.
10. Attach the servo arm to the camera body.
11. Insert the servo into the servo pillar and secure it with one of the bigger screws that came with the servo. Don't
attach the pillar just yet - the servo needs to be in the neutral position before it can be attached to the camera.
12. Connect the servo as follows:
    * Black - Pin 6
    * Red - Pin 4
    * White - Pin 32
12. Download the latest Watney release image and burn it onto the SD card.
13. Connect your Pi to the power bank. The servo should move to the neutral position when it's booted up. Power down
the Pi.
14. Carefully attach the camera body vertically to the servo.
15. Thread the camera cable through the body. Attach it to the camera. Secure the camera in the body with the cover.
16. Secure the servo pillar to the cover using a 12mm screw and a 16mm screw.
17. Secure the swivel pillar to the cover using same size screws.
18. Attach the camera body to the swivel column using a 12mm screw. Don't overtighten.
19. Attach your power bank to the top of the cover using double-sided tape, hot glue etc.
20. Make sure the rover is working. If one of the motors is spinning in the wrong direction, swap ForwardPin and 
ReversePin in ~/watney/rover.conf. Once everything is in order, secure the cover to the bottom using 12mm screws.


Configuration
-------------

Default credentials for Watney are pi / watney4. Watney's mDNS name is watney4.local.

Rover configuration can be found in ~/watney/rover.conf:
* If you want to use different GPIO pins, you can specify them here
* If you find a motor running in reverse (backwards when it's supposed to be rotating forward) simply swap ForwardPin and ReversePin
* Several advanced configuration values can be found there as well - modify at your own risk!