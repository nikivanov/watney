
<p align="center">
<a href="https://www.youtube.com/watch?v=a-NR-ddZKII"><img src="https://img.youtube.com/vi/a-NR-ddZKII/0.jpg" height="300"></img></a>
<img src="images/cad.png" height="300">
</p>

# Watney Rover
Watney is a low-cost, open source, Raspberry Pi-enabled telepresence rover made of readily available parts.
Non-electronic parts of Watney are 3D printable.
Watney provides a low-latency HD video feed as well as bi-directional audio.
Watney uses a wireless charging dock with passthrough charging so it can be left on indefinitely.

Watney uses the [Janus WebRTC Server](https://janus.conf.meetecho.com/) and [Raspberry Pi Turnkey](https://github.com/schollz/raspberry-pi-turnkey) 
 

# Components
Head over to [Bill of Materials](BOM.md) for a list of components you need to purchase to build your own Watney. You'll also need a 3D printer, some PETG / Tough PLA as well as TPU filament. Lastly, you'll need a soldering iron and some wires, though most connections are made using standard breadboard jumper wire.


# Assembly
Detailed [assembly instructions](ASSEMBLY.md) can be found here. One of the goals of developing Watney is to make it easy to assemble - like IKEA furniture of electronics. Go slow and double-check your work. Take extra caution not to reverse polarity when hooking up components, as most of them will burn out if hooked up in reverse. You'll be working with LiPol batteries - please be careful not to puncture or short them, as they can become a fire hazard if used improperly. **You assume all responsibility for damages that may be caused by your Watney, whether it's assembled correctly or otherwise.**

# Configuration
Upon startup, Watney will detect if it's connected to a Wi-Fi hotspot. If not, it will host its own hotspot "Watney4".
Once you connect to the hotspot, you can control it directly by going to https://192.168.4.1:5000, or connect it to a Wi-Fi
hotspot by going to http://192.168.4.1 Once you specify your WiFi credentials, Watney will take some time to reboot. Once you hear the startup sound, you're good to go!

Default SSH credentials for Watney are pi / watney4. Watney's mDNS name is watney4.local.

Watney's configuration can be found in ~/watney/rover.conf:
* If you want to use different GPIO pins, you can specify them here
* If you find motors on either side running in reverse (backwards when it's supposed to be rotating forward) simply swap ForwardPin 
and ReversePin
* Restart your Watney for configuration changes to take effect

# Remote Access
Watney has no authentication / security. If you'd like to set it up for remote access, I recommend using [Zerotier](https://www.zerotier.com/). Adding Watney and your client computer to the same Zerotier network will make it appear as if they are on the same local network.

# Troubleshooting
* Raspberry Pi has no ADC which means there's no way to read battery voltage without additional circuitry. However, an easy way to verify that your Watney is charging is to place the dock near a wall - you should be able to see the reflection of the glow from the charger via Watney's video feed.
* When camera moves up and down, you may notice stuttering / jitter. This happens because servo's PWM signal is generated in software. Since PWM is used for audio and PCM is used for I2S microphone, there are no more hardware interrupts for hardware-timed PWM signal generation. See Future Improvements for additional info.
* If you find your Watney randomly restarting when you move the camera, that means that the servo is drawing too much power from the Raspberry Pi. You can hook up the amplifier to one of the 3V outputs of the power board instead, and power the servo from the 5V output that was previously used by the amplifier.
* Watney works best with Chrome. Other browsers may not work well, or at all.
* Feel free to file an issue on GitHub if you have questions!

# Future Improvements
* **Better browser compatibility.** There's no reason it can't work in all major browsers.
* **Mobile-optimized control.** You'll be able to control your watney from your phone / tablet, especially in tandem with Remote Access.
* **Better volume scaling.** The volume slider is only usable at the top range - anything below 70% is barely audible. The slider should be scaled to control only the usable range instead.
* **Hardware-timed PWM.** Currently, PWM signal for motors and the camera servo are generated in software, which is the cause for the servo jitter. [pigpio](http://abyz.me.uk/rpi/pigpio/) is capable of generating very accurate hardware-timed PWM signals on any GPIO pin, but it needs either hardware PWM or PCM, both of which are used for audio. However, we only use one PWM channel for audio, so it may be possible to use the second channel for pigpio.
* **Timing Belts.** Coupling each pair of motors with a timing belt should greatly improve driving over very rough terrain.

# Setting up Remote Access with a TURN Server

_The following steps detail how to control the rover, runnning on your local network behind a firewal, from an external IP by relaying traffic through a TURN server._

Note: In examples some values will be enclosed with angle brackets (i.e. `<` and `>`). When replacing these values with your own you should replace the brackets as well. So the follwing...
```shell
ssh ubuntu@<YOUR IP ADDRESS>
```
should be...
```shell
ssh ubuntu@192.168.0.1
```

##  DDNS Configuration

_Will need to work with Drew to fill this in_

##  Setting up the TURN Server

_These instructions were taken directly from [How to Install Coturn - Buddhika Jayawardhana](https://meetrix.io/blog/webrtc/coturn/installation.html). They are reproduced here with slight modifications for fear of links breaking..._

_This guide assumes that you already have an AWS account and know how to deploy EC2 servers._

### Setting up the TURN Server

#### Deploying the EC2 Instance

1. From the EC2 Dashboard, select "Launch an Instance"
2. For the AMI choose Ubuntu (v20.04 LTS at the time of writing this guide)
3. For the instance type, a **t2.micro** should be sufficient.
4. Launch the server with key pairs that you have access to. You will need to use these later to SSH into the instance.
5. Nagivate back to the main instance dashboard. In the description tab in the bottom pane you should see a link for the instance's security group (e.g. 'launch-wizard-1'). Click this link.
6. Under "Inbound Rules" click "Edit Inbound Rules". Add the following rules.

| Port Range    | Transport Protocol | Notes                                |
|---------------|--------------------|--------------------------------------|
| 80            | TCP                | If you need to setup coturn with SSL |
| 443           | TCP                | If you need to setup coturn with SSL |
| 3478          | UDP                |                                      |
| 10000 - 20000 | UDP                |                                      |


#### Attaching an Elastic IP to the EC2 Instance

_If you're planning on communcating with your TURN server for longer than a day or so then you're going to want to configure an Elastic IP. This will allow you to swap the underlying EC2 instance without having to modify the IP address in Janus._

1. From the main EC2 dashboard click on the "Elastic IPs" link on the lefthand side (under Network and Security).
2. Click "Allocate Elastic IP Address"
3. Select "Amazon's pool of IPv4 addresses"
5. Click "Associate Elastic IP Address" and use the following values:
    - Resource Type: Instance
    - Instance: The ID of the instance you deployed in the previous step
    - Private IP Address: The private address of the instance you deployed
    - Reassociation: True

#### Installing Coturn on the server

1. SSH into the server
    
    _Use the elastic IP address that you associated in the previous step to test that it worked._

    ```shell
    ssh -i <YOUR PRIVATE KEY> ubuntu@<ELASTIC IP ADDRESS>
    ```

2. Install [Coturn](https://github.com/coturn/coturn) by running the following commands:
    ```shell
    sudo apt-get -y update
    sudo apt-get -y install coturn
    ```
3. Uncomment the following line in `/etc/default/coturn` (will need to edit with `sudo`)
    ```shell
    TURNSERVER_ENABLED=1
    ```
4. Configure the access credentials for your server by editing `/etc/turnserver.conf`. You may have to create this file. Add the following entries or replace existing values if they already exist.

    ```plaintext
    realm=<CUSTOM REALM NAME>
    fingerprint
    listening-ip=0.0.0.0
    external-ip=<EXTERNAL_IP>/<INTERNAL_IP> #or just the external ip
    listening-port=3478
    min-port=10000
    max-port=20000
    log-file=/var/log/turnserver.log
    verbose

    user=<TURN_CUSTOM_USERNAME>:<TURN_CUSTOM_PASSWORD>
    lt-cred-mech
    ```

    - The `CUSTOM REALM NAME` can be anything you want. I would stay way from weird characters and just use periods and alphanumeric chars.
    - `EXTERNAL IP` will be the Elastic IP address of your EC2 server.
    - `INTERNAL IP` can be found in the "Description" tab for your EC2 instance in the dashboard. It will be listed as `Private IPs` there.
5. Restart the service for your changes to take effect.
    ```shell
    sudo service coturn restart
    ```

## Configuring Janus on the Watney Server

1. SSH into your Watney rover.
2. Run the following commands create a symbolic link to the config file in our watney folder.

    ```shell
    #   Backup the current Janus config in case we mess something up
    sudo mv /opt/janus/etc/janus/janus.jcfg /opt/janus/etc/janus/janus/janus.jcfg.bak

    #   Create a symbolic link to the janus configuration in the Watney server.
    #   Any changes made there will now have an effect.
    sudo ln -s ~/watney/janus/janus.jcfg /opt/janus/etc/janus/janus.jcfg
    ```

2. Set the following values in `~/watney/janus/janus.jcfg`. These will be the same values you set in the previous section when setting up your EC2 TURN server.
    ```plaintext
    turn_server = "<YOUR ELASTIC IP ADDRESS>"
    turn_port = 3478
    turn_type = "udp"
    turn_user = "<TURN_CUSTOM_USERNAME>"
    turn_pwd = "<TURN_CUSTOM_PASSWORD>"
    ```
3. Also set these values in `~/watney/js/watney_janus.js`:
    ```javascript
    const iceServers = [{
        urls: "turn:<YOUR ELASTIC IP ADDRESS>",
        username: "<TURN_CUSTOM_USERNAME>",
        credential: "<TURN_CUSTOM_PASSWORD>"
    }] 
    ```
