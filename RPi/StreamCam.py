# Threaded class that controls the camera stream

import cv2
from threading import Thread
import time

class StreamCam:
        def __init__(self, resolution=(1280,720), framerate=30, src=0, display=False):
                self.stream = cv2.VideoCapture(src)
                self.stream.set(3, resolution[0])
                self.stream.set(4, resolution[1])
                self.resume()
                self.display = display
                self.stopping = False
                self.running = False
                self.frame = []
                self.framerate = framerate
                self.dtime = 1000/framerate
                self.lastgrab = self.__gettime()

        # Used for dtime
        def __gettime(self):
                return time.time() * 1000

        # Pause running the loop
        def pause(self):
                self.streaming = False

        # Resume running the loop
        def resume(self):
                self.streaming = True

        # Primary loop for display
        def loop(self):
                while True:
                        if self.stopping:
                                self.stream.release()
                                return
                        if self.streaming:
                                self.pullframe()
                        if self.display and len(self.frame) > 0:
                                cv2.imshow('StreamCam Debug', self.frame)
                                if cv2.waitKey(1) == 27:
                                        self.edit(False)
                        time.sleep(self.dtime/1000) # No point looping during the camera lock

        # Stop the camera stream
        def stop(self):
                self.stopping = True

        # Start the camera. Only use during creation
        def start(self):
                if not self.running:
                        self.running = True
                        Thread(target=self.loop).start()
                        return self

        # Edit settings - currently just Display
        def edit(self, display):
                self.display = display
                if not display:
                        cv2.destroyWindow('StreamCam Debug')

        # Pull a new frame & return it
        def pullframe(self):
                # A delay is introduced in order to avoid issues with pulling frames too quickly
                if self.__gettime() > self.lastgrab + self.dtime:
                        ret, img = self.stream.read()
                        if ret:
                                self.frame = img
                return self.frame

        # Return the most recent frame
        def curframe(self):
                return self.frame

