from threading import Thread, Condition
import shlex
import subprocess


class TTSSpeaker:
    def __init__(self, ttsCommand):
        self.shuttingDown = False
        self.ttsCommand = ttsCommand
        self.workQueueLock = Condition()
        self.workQueue = []
        self.speakingThread = Thread(daemon=True, target=self.speakingLoop)
        self.speakingThread.start()

    def speakingLoop(self):
        print("TTS starting...")
        while True:
            with self.workQueueLock:
                if len(self.workQueue) == 0:
                    self.workQueueLock.wait()

                if self.shuttingDown:
                    break

                if len(self.workQueue) > 0:
                    currentPhrase = self.workQueue[0]
                    self.workQueue.pop(0)
                else:
                    currentPhrase = None

            if currentPhrase is not None:
                fullTTSCommand = self.ttsCommand.format(shlex.quote(currentPhrase))
                ttsArgs = shlex.split(fullTTSCommand)
                subprocess.call(ttsArgs)

        print("TTS stopping...")

    def addPhrase(self, phrase):
        with self.workQueueLock:
            self.workQueue.append(phrase)
            self.workQueueLock.notify()

    def stop(self):
        with self.workQueueLock:
            self.shuttingDown = True
            self.workQueueLock.notify()

        print("Joining the TTS thread")
        self.speakingThread.join()
        print("TTS thread stopped")
