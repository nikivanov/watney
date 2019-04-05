from quart import Quart, send_file, request, send_from_directory, jsonify
import hypercorn
from motorcontroller import MotorController
from servocontroller import ServoController
from heartbeat import Heartbeat
from subprocess import call
import asyncio
from signaling import SignalingServer
import os
import pigpio
from configparser import ConfigParser
from alsa import Alsa

app = Quart(__name__)
motorController = None
servoController = None
heartbeat = None
signalingServer = None
alsa = None


@app.route("/")
async def getPageHTML():
    return await send_file("index.html")


@app.route('/js/<path:path>')
async def send_js(path):
    return await send_from_directory('js', path)


@app.route("/sendCommand", methods=['POST'])
async def setCommand():
    commandObj = await request.get_json()
    newBearing = commandObj['bearing']
    newLook = commandObj['look']

    if newBearing in MotorController.validBearings:
        motorController.setBearing(newBearing)
    else:
        print("Invalid bearing {}".format(newBearing))
        return "Invalid", 400

    if newLook == 0:
        servoController.lookStop()
    elif newLook == -1:
        servoController.forward()
    elif newLook == 1:
        servoController.backward()
    else:
        print("Invalid look at {}".format(newLook))
        return "Invalid", 400

    return "OK"


@app.route("/shutDown", methods=['POST'])
async def shutdown():
    call("halt", shell=True)


@app.route("/sendTTS", methods=['POST'])
async def sendTTS():
    ttsObj = await request.get_json()
    ttsString = ttsObj['str']
    roverDriver.sayTTS(ttsString)
    return "OK"


@app.route("/setVolume", methods=['POST'])
async def setVolume():
    volumeObj = await request.get_json()
    volume = int(volumeObj['volume'])
    alsa.setVolume(volume)
    return "OK"


@app.route("/heartbeat", methods=['POST'])
async def onHeartbeat():
    stats = heartbeat.onHeartbeatReceived()
    return jsonify(stats)


if __name__ == "__main__":
    homePath = os.path.dirname(os.path.abspath(__file__))
    pi = pigpio.pi()

    config = ConfigParser()
    config.read(os.path.join(homePath, "rover.conf"))

    signalingServer = SignalingServer()
    signalingServer.start()

    motorController = MotorController(pi, config)

    alsa = Alsa(pi, config)

    servoController = ServoController(pi, config)
    servoController.start()

    heartbeat = Heartbeat(config, servoController, motorController, alsa)
    heartbeat.start()

    loop = asyncio.get_event_loop()

    try:
        app.run(host='0.0.0.0', port=5000, debug=False, certfile='cert.pem', keyfile='key.pem', loop=loop)
    finally:
        alsa.stop()
        heartbeat.stop()
        servoController.stop()

        pending = asyncio.Task.all_tasks()
        try:
            loop.run_until_complete(asyncio.gather(*pending))
        except hypercorn.utils.Shutdown:
            pass