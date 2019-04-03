from quart import Quart, send_file, request, send_from_directory, jsonify
import json
# from rover import Driver
import signal
import sys
#from rover import MotorController
from subprocess import call
import logging
import asyncio
from signaling import SignalingServer

app = Quart(__name__)
roverDriver = None
signalingServer = None


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
        if newBearing == "0":
            roverDriver.stop()
        else:
            roverDriver.setBearing(newBearing)
    else:
        print("Invalid bearing {}".format(newBearing))
        return "Invalid", 400

    if newLook == 0:
        roverDriver.lookStop()
    elif newLook == -1:
        roverDriver.lookUp()
    elif newLook == 1:
        roverDriver.lookDown()
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
    roverDriver.setVolume(volume)
    return "OK"


@app.route("/heartbeat", methods=['POST'])
async def onHeartbeat():
    stats = roverDriver.onHeartbeat()
    return jsonify(stats)


def signal_handler(signal, frame):
    asyncio.get_event_loop().stop()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    ssl_context=('cert.pem', 'key.pem')
    signalingServer = SignalingServer()
    signalingServer.start()
    # roverDriver = Driver()
    app.run(host='0.0.0.0', port=5000, debug=False, certfile='cert.pem', keyfile='key.pem')
