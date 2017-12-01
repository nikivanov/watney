Watney Rover
------------

Watney is a low-cost Raspberry Pi-enabled rover made of readily available parts. At the heart of it is
Raspberry Pi Zero W powered by a small phone battery bank. Two 28byj-48
stepper motors provide direct drive to rear wheels and rear wheel
steering. Stepper motor drivers draw power directly from RPi's 5V GPIO pins.
RPi V2 camera is mounted on an adjustable arm on the front of the rover.
If you go with a solderless header, there's no soldering needed for assembly.


Besides the components listed above, some breadboard jumper wires and M3
screws, the rest of the components are 3D-printable. All parts are fairly small
and should be printable on even cheapest 3D printers.

The software part of Watney is written in Python and provides webcam-on-wheels
functionality. The camera feed is hardware-encoded to allow low-latency streaming in 720p.
A web page containing keyboard controls and the camera stream can be accessed by navigating
to Watney's IP in a browser.


Ingredients
------------

If you're lucky enough to live near a Microcenter, most of these items can be found there.
The rest can be easily found on Amazon

* Raspberry Pi Zero W
* 40 pin header (either regular or solderless)
* Raspberry Pi Camera V2
* RPi Zero-compatible camera ribbon cable
* USB power bank that provides at least 800ma, like Inland 2,600mAh Power Bank
* 2x 28byj-48 stepper motors with drivers (they almost always come with drivers)
* 12x 10cm Female-to-female jumper wires