Watney Rover
------------

![watney](https://i.imgur.com/ZHjlQ2Y.gifv)

Watney is a low-cost Raspberry Pi-enabled rover made of readily available parts. At the heart of it is
Raspberry Pi Zero W powered by a small phone battery bank. Two 28byj-48
stepper motors provide direct drive to rear wheels and an RPi camera is mounted in the front.
If you go with a solderless header, there's no soldering needed for assembly.


Besides the components listed above, some breadboard jumper wires and M3
screws, the rest of the components are 3D-printable. Biggest parts are 120mm long
so pretty much any 3D printer could do it.

The software part of Watney is written in Python and provides webcam-on-wheels
functionality. The camera feed is low-latency 720p and you control the rover from the browser.


Ingredients
------------


* Raspberry Pi Zero W
* 40 pin header (either regular or solderless)
* Raspberry Pi Camera V2
* RPi Zero-compatible camera ribbon cable
* USB power bank that provides at least 800ma, like Anker PowerCore+ mini
* 2x 28byj-48 stepper motors with drivers (they almost always come with drivers)
* 12x 10cm Female-to-female jumper wires