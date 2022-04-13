# Testing out OpenCV's ability to trace card identifiers.

import StreamCam
import cv2
import numpy as np
import time

stream = StreamCam.StreamCam().start()
stream.pause()

MAX_DEGREE_VAR = 15

MIN_PER = 10
MAX_PER = 25

# This was adapted from a Playing Card Detector by EdjeElectronics
def sortcontours(contours, hierarchy):
        sorted_stuff = sorted(range(len(contours)), key=lambda i : cv2.contourArea(contours[i]),reverse=True)

        sorted_contours = []
        sorted_hierarchies = []

        accepted_contours = []

        hold_contours = []
        hold_hierarchies = []

        for i in sorted_stuff:
                sorted_contours.append(contours[i])
                sorted_hierarchies.append(hierarchy[0][i])

        for i in range(len(sorted_contours)):
                area = cv2.contourArea(sorted_contours[i])
                perimeter = cv2.arcLength(sorted_contours[i],True)
                approx = cv2.approxPolyDP(sorted_contours[i],0.1*perimeter,True)
                ((x, y), (w, h), angle) = cv2.minAreaRect(approx)
                if (w > 0 and h > 0): # Has a rect around it
                        ratio = w / float(h) # Aspect ratio
                        if len(approx) == 4 and (area > MIN_PER * MIN_PER and area < MAX_PER * MAX_PER): # Has 4 sides and an acceptable area
                                if (perimeter > MIN_PER * 4 and perimeter < MAX_PER * 4) and (ratio > 0.8 and ratio < 1.2): # Is square-ish and has an acceptable perimeter
                                        if angle > 0 - (MAX_DEGREE_VAR / 2) or angle < -90 + (MAX_DEGREE_VAR / 2): # Allow only defined variation in orientation
                                                hold_contours.append(sorted_contours[i])
                                                hold_hierarchies.append(sorted_hierarchies[i])

        # Make sure only the innermost square is used
        for i in range(len(hold_contours)):
                if hold_hierarchies[i][2] == -1:
                        accepted_contours.append(hold_contours[i])

        return accepted_contours

while True:
        img = stream.pullframe()
        if len(img) > 0:
                imggray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                rows, cols = map(int, imggray.shape)

                imgfiltered = cv2.GaussianBlur(imggray,(3,3),0) # Blur to make it easier to find the contours
                #imgfiltered = cv2.pyrDown(imggray, dstsize=(cols // 8, rows // 8))
                #imgfiltered = cv2.pyrUp(imgfiltered, dstsize=(cols, rows))

                thresh = cv2.adaptiveThreshold(imggray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,19,5)

                im2, contoursOld, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contours = sortcontours(contoursOld, hierarchy)

                cv2.imshow('testy noodle', imgfiltered)

                imgtoshow = img
                imgtoshow = cv2.drawContours(imgtoshow, contours, -1, (0,255,0), 3) # show green (identified squares)
                imgtoshow = cv2.drawContours(imgtoshow, contoursOld, -1, (255,0,0), 1) # show blue (all contours)

                cv2.imshow('testy doodle', imgtoshow)
                if cv2.waitKey(1) == 27:
                        time.sleep(20)

stream.stop()
