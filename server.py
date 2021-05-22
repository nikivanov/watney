from audiomanager import AudioManager
from powerplant import PowerPlant
from aiohttp import web
from motorcontroller import MotorController
from servocontroller import ServoController
from lightscontroller import LightsController
from heartbeat import Heartbeat
from subprocess import call
import os
import pigpio
from configparser import ConfigParser
from alsa import Alsa
import ssl
import sys
from externalrunner import ExternalProcess
import asyncio
from janusmonitor import JanusMonitor
from tts import TTSSpeaker
from startupSequence import StartupSequenceController

routes = web.RouteTableDef()

motorController = None
servoController = None
heartbeat = None
signalingServer = None
alsa = None
tts = None
powerPlant = None
startupController = None
audioManager = None
audioManagerThread = None

@routes.get("/")
async def getPageHTML(request):
    return web.FileResponse("index.html")


@routes.post("/sendCommand")
async def setCommand(request):
    commandObj = await request.json()
    newBearing = commandObj['bearing']
    newLook = commandObj['look']
    newSlow = commandObj['slow']

    if newBearing in MotorController.validBearings:
        motorController.setBearing(newBearing, newSlow)
    else:
        print("Invalid bearing {}".format(newBearing))
        return web.Response(status=400, text="Invalid")

    if newLook == 0:
        await servoController.lookStop()
    elif newLook == -1:
        await servoController.forward()
    elif newLook == 1:
        await servoController.backward()
    else:
        print("Invalid look at {}".format(newLook))
        return web.Response(status=400, text="Invalid")

    return web.Response(text="OK")


@routes.post("/shutDown")
async def shutDown(request):
    call("sudo halt", shell=True)

@routes.post("/restart")
async def restart(request):
    call("sudo reboot", shell=True)


@routes.post("/sendTTS")
async def sendTTS(request):
    ttsObj = await request.json()
    ttsString = ttsObj['str']
    tts.sayText(ttsString)
    return web.Response(text="OK")


@routes.post("/setVolume")
async def setVolume(request):
    volumeObj = await request.json()
    volume = int(volumeObj['volume'])
    alsa.setVolume(volume)
    return web.Response(text="OK")


@routes.post("/heartbeat")
async def onHeartbeat(request):
    stats = heartbeat.onHeartbeatReceived()
    return web.json_response(stats)

@routes.post("/lights")
async def onLights(request):
    lightsObj = await request.json()
    on = bool(lightsObj['on'])
    if on:
        lightsController.lightsOn()
    else:
        lightsController.lightsOff()
    return web.Response(text="OK")


# Python 3.7 is overly wordy about self-signed certificates, so we'll suppress the error here
def loopExceptionHandler(loop, context):
    exception = context.get('exception')
    if isinstance(exception, ssl.SSLError) and exception.reason == 'SSLV3_ALERT_CERTIFICATE_UNKNOWN':
        pass
    else:
        loop.default_exception_handler(context)


def createSSLContext(homePath):
    # Create an SSL context to be used by the websocket server
    print('Using TLS with keys in {!r}'.format(homePath))
    chain_pem = os.path.join(homePath, 'cert.pem')
    key_pem = os.path.join(homePath, 'key.pem')
    sslctx = ssl.create_default_context()

    try:
        sslctx.load_cert_chain(chain_pem, keyfile=key_pem)
    except FileNotFoundError:
        print("Certificates not found, did you run generate_cert.sh?")
        sys.exit(1)
    # FIXME
    sslctx.check_hostname = False
    sslctx.verify_mode = ssl.CERT_NONE
    return sslctx


if __name__ == "__main__":
    homePath = os.path.dirname(os.path.abspath(__file__))
    sslctx = createSSLContext(os.path.dirname(homePath))

    gpio = pigpio.pi()
    if not gpio.connected:
        print('GPIO not connected')
        exit()
    
    config = ConfigParser()
    config.read(os.path.join(homePath, "rover.conf"))
    audioConfig = config["AUDIO"]
    videoConfig = config["VIDEO"]

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(loopExceptionHandler)

    audioManager = AudioManager(config)
    audioManager.start()

    motorController = MotorController(config, gpio, audioManager)

    alsa = Alsa(gpio, config)

    servoController = ServoController(gpio, config, audioManager)
    lightsController = LightsController(gpio, config)

    tts = TTSSpeaker(config, alsa, audioManager)

    powerPlant = PowerPlant(config)

    startupController = StartupSequenceController(config, servoController, lightsController, tts)

    heartbeat = Heartbeat(config, servoController, motorController, alsa, lightsController, powerPlant)
    heartbeat.start()

    janus = ExternalProcess(videoConfig["JanusStartCommand"], False, False, "janus.log")
    videoStream = ExternalProcess(videoConfig["GStreamerStartCommand"], True, False, "video.log")

    janusMonitor = JanusMonitor()
    janusMonitor.start()

    app = web.Application()
    app.add_routes(routes)
    app.router.add_static('/js/', path=os.path.join(homePath, 'js'))

    web.run_app(app, host='0.0.0.0', port=5000, ssl_context=sslctx)

    servoController.stop()
    lightsController.stop()
    gpio.stop()

