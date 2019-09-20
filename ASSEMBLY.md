# Assembly
## Notes
None of the 3D printed parts require supports. I recommend printing in PETG, or at least Tough PLA. Tires need to be printed in TPU. In most cases, you need to drive M3 bolts directly into the holes in plastic. If you're having trouble getting the bolt to go in when securing a part, prime the hole with a bolt for a few millimeters and then try again. Don't overtighten.
## Base Part
<a href="images/assembly/charger.jpg"><img src="images/assembly/charger.jpg" height="256"></a>
<a href="images/assembly/wireless_client.jpg"><img src="images/assembly/wireless_client.jpg" height="256"></a>
<a href="images/assembly/motors.jpg"><img src="images/assembly/motors.jpg" height="256"></a>

1. Break off 6 pairs of pin headers and solder them to the Dual 18650 board
1. Insert 18650 batteries. Ensure the correct polarity, or you will burn out the board
1. Connect the wireless charger to a 2A USB power supply
1. Connect the wireless client to the extension cable, and then plug the cable into the charging port of the board. Place the cient onto the charger and make sure it starts charging
1. Print out bottom.stl, 4x motor holder.stl, charger client holder.stl.
1. Place the charger client onto the bottom and place the charger client holder on top of it. Push the holder into the bottom and secure it with 6mm bolts.
1. Attach the Micro USB extension cable to the charger client.
1. Solder about 15cm of wire to each motor and then connect the other ends in parallel. Make sure not to reverse polarity, or the motors will spin in different directions. I recommend soldering with wires pointing towards the axle.
1. Drive an M3 nut into slots of each motor holder, 8 total.
1. Place each motor into its slot, as shown in the picture. Place a motor holder over each motor and align the holes. Use 8mm bolts from the outside to pull each holder to the wall. Make sure all motors are in held in place.
1. Insert the motor wire leads into L298N H-Bridge. Polarity here doesn't matter much because we'll be able to set it in the config later.
1. Gently place L298N onto the mounting holes in the bottom and secure it with 6mm bolts. You should only need to use 2 bolts.
1. Attach a pair of 30cm MF Dupont wires to the 12V and GND of L298N. Make sure you're not attaching to the 5V - it's an output.

