import subprocess
import shlex
import sys
from threading import Thread
import time
import signal


class ExternalRunner:
    
    def __init__(self):
        self.processes = list()
        self.shuttingDown = False
        self.workerThread = Thread(target=self.doWork, daemon=True)
        self.workerThread.start()

    def addExternalProcess(self, command, shell, restartOnExit):
        commandArgs = shlex.split(command)
        process = subprocess.Popen(commandArgs, stdout=sys.stdout, stderr=sys.stderr, shell=shell)
        externalProcess = ExternalProcess(process, restartOnExit, shell)
        self.processes.append(externalProcess)
        print("Added process: " + str(commandArgs))

    def doWork(self):
        while not self.shuttingDown:
            for process in self.processes:
                if process.restartOnExit and process.process.poll() is not None:
                    # horrible hack - external processes capture their own CTRL-C. External Runner is the first
                    # to perform cleanup, but it still might be in a race condition
                    time.sleep(0.1)
                    if not self.shuttingDown:
                        print("Restarting process: " + str(process.process.args))
                        process.process = subprocess.Popen(process.process.args, stdout=sys.stdout, stderr=sys.stderr, shell=process.shell)

            time.sleep(0.5)

        for process in self.processes:
            print("Shutting down process: " + str(process.process.args))
            process.process.terminate()

        print("All external processes shut down")

    def shutdown(self):
        print("Shutting down external runner")
        self.shuttingDown = True
        self.workerThread.join()


class ExternalProcess:
    def __init__(self, process, restartOnExit, shell):
        self.process = process
        self.restartOnExit = restartOnExit
        self.shell = shell


