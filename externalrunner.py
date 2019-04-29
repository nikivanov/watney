from events import Events
import shlex
import asyncio


class ExternalProcess:
    def __init__(self, command, sessionBased):
        self.command = command
        self.task = None
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
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.__startProcess())

    async def __startProcess(self):
        print('Executing \'{}\''.format(self.command))
        try:
            process = await asyncio.create_subprocess_shell(self.command)
            await process.communicate()
            self.task = None
        except asyncio.CancelledError:
            pass

    def endProcess(self):
        if self.task is not None and not self.task.done():
            self.task.cancel()
