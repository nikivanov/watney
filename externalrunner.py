import subprocess
import shlex
import sys
from threading import Thread
import time
import os
import signal


class ExternalRunner:

    def __init__(self, janusMonitor):
        janusMonitor.addWatcher(lambda sessionPresent: self.handleSessionChange(sessionPresent))
        self.processes = list()
        self.shuttingDown = False
        self.sessionPresent = False
        self.workerThread = Thread(target=self.doWork, daemon=True)
        self.workerThread.start()

    def addExternalProcess(self, command, shell, restartOnExit, sessionBased):
        commandArgs = shlex.split(command)
        if not sessionBased or self.sessionPresent:
            process = self.startProcess(commandArgs, shell)
        else:
            process = None
        externalProcess = ExternalProcess(process, commandArgs, restartOnExit, shell, sessionBased)
        self.processes.append(externalProcess)
        print("Added process: " + str(commandArgs))

    def doWork(self):
        while not self.shuttingDown:
            sessionPresent = self.sessionPresent
            for process in self.processes:
                # kill the process if it's session based and session is not present and process is started
                kill = process.sessionBased and not sessionPresent and process.process is not None
                # start the process if EITHER it's session based, the session is present and the process has not been
                # started or has crashed and is designated for restarts, OR it's not session-based, has crashed and is
                # designated for restarts
                start = (process.sessionBased and sessionPresent and (process.process is None or (
                        process.process.poll() is not None and process.restartOnExit))) or (
                                not process.sessionBased and process.restartOnExit and process.process.poll() is not None)

                if kill:
                    print("Shutting down process: " + str(process.args))
                    os.killpg(os.getpgid(process.process.pid), signal.SIGTERM)
                    process.process = None
                elif start:
                    # horrible hack - external processes capture their own CTRL-C. External Runner is the first
                    # to perform cleanup, but it still might be in a race condition
                    time.sleep(0.1)
                    if not self.shuttingDown:
                        print("Starting process: " + str(process.args))
                        process.process = self.startProcess(process.args, process.shell)

            time.sleep(0.5)

        for process in self.processes:
            if process.process is not None:
                print("Shutting down process: " + str(process.args))
                os.killpg(os.getpgid(process.process.pid), signal.SIGTERM)

        print("All external processes shut down")

    def startProcess(self, commandArgs, shell):
        return subprocess.Popen(commandArgs, stdout=sys.stdout, stderr=sys.stderr, shell=shell, preexec_fn=os.setsid)

    def handleSessionChange(self, sessionPresent):
        self.sessionPresent = sessionPresent

    def shutdown(self):
        print("Shutting down external runner")
        self.shuttingDown = True
        self.workerThread.join()


class ExternalProcess:
    def __init__(self, process, args, restartOnExit, shell, sessionBased):
        self.process = process
        self.args = args
        self.restartOnExit = restartOnExit
        self.shell = shell
        self.sessionBased = sessionBased
