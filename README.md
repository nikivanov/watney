Watney Rover
------------


<p align="center">
  <img width="45%" height="auto" src="images/watney.png?raw=true">
  <img width="45%" height="auto" src="images/watney-nocover.png?raw=true">
  <br />
  <img width="90%" height="auto" src="images/watney-photo.jpg?raw=true">
</p>


[Video](https://i.imgur.com/vydmPej.gifv)


Watney is a low-cost Raspberry Pi-enabled rover made of readily available parts. At the heart of it is
Raspberry Pi Zero W powered by a small phone battery bank. Two motors and a controller
provide direct drive to rear wheels and an RPi camera is mounted in the front.
Very little to no soldering required. The driving library is written in Python.


Besides the components listed above, some breadboard jumper wires and M3
screws, the rest of the components are 3D-printable.

The software part of Watney provides webcam-on-wheels functionality. The camera feed is low-latency HD and you control the rover from your browser.


Components
------------


* **Raspberry Pi Zero W**
If you live near a MicroCenter in the US, you could get one of these for $5. You also obviously need an SD card.
* **Raspberry Pi Camera with Zero-compatible cable**
I used a Raspberry Pi Camera v2, but you can get a cheap cameras on ebay for about $9 if you search for "raspberry pi zero camera"
* **USB power bank that provides at least 800ma**
Bigger is better as long as it fits on the roof
* **2x Arduino geared DC motors** ([Amazon](http://a.co/7sPakWM) | [AliExpress](https://www.aliexpress.com/item/TT-Motor-Smart-Car-Robot-Gear-Motor-for-Arduino-Free-Shipping/32529098435.html))
* **L298N H-bridge controller** ([Amazon](http://a.co/1fvKKte) | [AliExpress](https://www.aliexpress.com/item/Free-Shipping-New-Dual-H-Bridge-DC-Stepper-Motor-Drive-Controller-Board-Module-L298N-MOTOR-DRIVER/32769190826.html))
* **Jumper wire 10cm or longer**
* **M3 screws**

The major components (minus wire and screws) can be bought for around $40 depending on where you live.


Assembly
--------
![Wiring](images/Wiring.jpg?raw=true)
