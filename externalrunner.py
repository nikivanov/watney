import subprocess
import shlex

class ExternalRunner:
    
    def __init__(self):
        self.processMap = dict()

    def addExternalProcess(self, command, restartOnExit):
        commandArgs = shlex.split(command)
        process = ExternalProcess(command, restartOnExit)
         


class ExternalProcess:
    def __init__(self, commandArgs, restartOnExit):
        self.commandArgs = commandArgs
        self.restartOnExit = restartOnExit