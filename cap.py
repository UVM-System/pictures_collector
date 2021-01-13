#!/usr/bin/python3
import cv2
import threading
class CapHandler(object):
    def __init__(self,video_order):
        self.frame = None
        self.start = False
        self.stop = False
        self.cap_handler = cv2.VideoCapture(video_order)
    
    def run(self):
        while not self.stop:
            ret,frame = self.cap_handler.read()
            if ret:
               self.frame = frame 

    def startCap(self):
        self.start = True
        self.stop = False
        threadHandler = threading.Thread(target=self.run)
        threadHandler.start()
    def stop(self):
        self.stop = True
        self.start = False
    def getFrame(self):
        return self.frame

if __name__=="__main__":
    cap = CapHandler(0)
    cap.startCap()

    while True:
        input_str = input("input!\n")
        if input_str=="c":
            cv2.imshow("cap",cap.getFrame())
            cv2.waitKey()
        if input_str=="q":
            exit()
        