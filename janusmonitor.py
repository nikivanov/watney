import asyncio
import aiohttp
import uuid
from events import Events


class JanusMonitor:
    def __init__(self):
        self.hasOpenSession = False
        self.task = None
        self.client = aiohttp.ClientSession()

    def start(self):
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.monitorLoop())

    def stop(self):
        if self.client:
            self.client.close()

        if self.task:
            self.task.cancel()

    async def monitorLoop(self):
        print("Starting Janus monitor...")
        lastRequestFailed = False
        firstTime = True
        try:
            while True:
                try:
                    response = await self.client.post("http://localhost:7088/admin", json={
                        "janus": "list_sessions",
                        "transaction": str(uuid.uuid4()),
                        "admin_secret": "janusoverlord"
                    })
                    lastRequestFailed = False

                    if firstTime:
                        print("Janus monitor connected to Janus...")
                        firstTime = False

                    async with response:
                        await self.handleSessionsObject(response)

                except Exception as e:
                    if not lastRequestFailed and not firstTime:
                        print("Janus session request failed: " + str(e))
                    lastRequestFailed = True

                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print("Janus monitor stopped")
        except Exception as e:
            print("Unexpected exception in Janus monitor: " + str(e))

    async def handleSessionsObject(self, response):
        responseObj = await response.json()
        sessionPresent = len(responseObj["sessions"]) > 0
        if sessionPresent != self.hasOpenSession:
            self.hasOpenSession = sessionPresent
            print("Session presence: " + str(self.hasOpenSession))
            if sessionPresent:
                Events.getInstance().fireSessionStarted()
            else:
                Events.getInstance().fireSessionEnded()
