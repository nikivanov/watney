from events import Events
import asyncio
import os
import signal


class ExternalProcess:
    def __init__(self, command, sessionBased, restartOnExit, logName=None):
        self.command = command
        self.task = None
        self.process = None
        self.restartOnExit = restartOnExit
        self.logName = logName
        self.terminating = False

        if sessionBased:
            Events.getInstance().sessionStarted.append(lambda: self.onSessionStarted())
            Events.getInstance().sessionEnded.append(lambda: self.onSessionEnded())
        else:
            self.startProcess()

    def onSessionStarted(self):
        self.startProcess()

    def onSessionEnded(self):
        self.endProcess()

    def startProcess(self):
        self.terminating = False
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.__startProcess())

    async def __startProcess(self):
        print('Executing \'{}\''.format(self.command))
        logFilePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.logName)
        print("Logging to \'{}\'".format(logFilePath))
        with open(logFilePath, 'w') as logFile:
            try:
                self.process = await asyncio.create_subprocess_shell(self.command, stdout=logFile, stderr=logFile, start_new_session=True)
                await self.process.communicate()
                print("Process \'{}\' finished".format(self.command))
                self.task = None
                self.process = None
                if self.restartOnExit and not self.terminating:
                    print("Restarting \'{}\'".format(self.command))
                    self.startProcess()
            except asyncio.CancelledError:
                print('Terminated \'{}\''.format(self.command))
                if self.process is not None:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.task = None
                self.process = None

    def endProcess(self):
        print("Terminating \'{}\'".format(self.command))
        if self.process is not None:
            self.terminating = True
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
