from flask import Flask, send_file, request, send_from_directory
import json
from rover import Driver
import signal
import sys
import os


app = Flask(__name__)
roverDriver = None


@app.route("/")
def getPageHTML():
    return send_file("index.html")


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route("/sendBearing", methods = ['POST'])
def setBearing():
    bearingObj = json.loads(request.data.decode("utf-8"))
    newBearing = bearingObj['bearing']

    if newBearing == -1:
        roverDriver.stop()
    else:
        roverDriver.setBearing(newBearing)

    return "OK"

def signal_handler(signal, frame):
    os.system("pkill uv4l")
    roverDriver.cleanup()
    sys.exit(0)

def startVideo():
    print("Starting video feed...")
    os.system("sudo service rws restart")
    # os.system('./startVideo.sh')


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    startVideo()
    roverDriver = Driver()
    app.run(host='0.0.0.0', port=5000, debug=False)
