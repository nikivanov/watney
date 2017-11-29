Watney Rover
------------

Watney is a low-cost, Raspberry Pi-enabled rover. At the heart of it is
Raspberry Pi Zero W powered by a small phone battery bank. Two 28byj-48
stepper motors provide direct drive to rear wheels and rear wheel
steering. Stepper motor drivers draw power directly from RPi's 5V GPIO pins.
RPi V2 camera is mounted on an adjustable arm on the front of the rover.

Besides the components listed above, some breadboard jumper wires and M3
screws, the rest of the components are 3D-printable. All parts are fairly small
and should be printable on even cheapest 3D printers.

The software part of Watney is written in Python and provides webcam-on-wheels
functionality. The camera feed is hardware-encoded into an HD stream, which is served
on a web page that also provides keyboard control of the rover.
