import os
import cv2
import math
import numpy as np

##Resize with resize command
def resizeImage(img,ratio):
    dst = cv2.resize(img,None, fx=ratio, fy=ratio, interpolation = cv2.INTER_LINEAR)
    return dst

##Take image with Raspberry Pi camera
os.system("raspistill -w 2592 -h 1944 -ex verylong -o /home/pi/Desktop/flux-pi/image.jpg")

##Load image
#img = cv2.imread("/home/pi/Desktop/flux-pi/image.jpg") 
#grey = cv2.imread("/home/pi/Desktop/flux-pi/image.jpg",0) #0 for grayscale

frame=cv2.imread('/home/pi/Desktop/flux-pi/image.jpg')
#img=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


#grey = cv2.imread("/home/pi/Desktop/flux-pi/image.jpg",0) #0 for grayscale
#img = cv2.GaussianBlur(frame, (1,1), 0)

##Run Threshold on image to make it black and white
ret, thresh = cv2.threshold(frame,50,255,cv2.THRESH_BINARY)

lower=np.array([0, 0, 0],np.uint8)
upper=np.array([10, 50, 50],np.uint8)
separated=cv2.inRange(thresh,lower,upper)

##Find outer squares using contours
squares = []
contours,hierarchy=cv2.findContours(separated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
for idx, contour in enumerate(contours):
    moment = cv2.moments(contour)
    if moment["m00"] > 1000:
        rect = cv2.minAreaRect(contour)
        rect = ((rect[0][0], rect[0][1]), (rect[1][0], rect[1][1]), rect[2])
        (width,height)=(rect[1][0],rect[1][1])
        print str(width)+" "+str(height)
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)
        if(height>0.8*width and height<1.2*width):
            squares.append(rect)
            cv2.drawContours(thresh,[box], 0, (0, 0, 255), 2)

print "idx: " + str(idx)
print "Found squares: " + str(len(squares))

#for idx_s, square in enumerate(squares):
    #tmp_crop = separated[rect[0][0]:rect[0][1], rect[1][0]:rect[1][1]]

    #ret, thresh_tmp = cv2.threshold(tmp_crop,50,255,cv2.THRESH_BINARY)

    #lower=np.array([0, 0, 0],np.uint8)
    #upper=np.array([10, 50, 50],np.uint8)
    #separated_tmp = cv2.inRange(thresh_tmp,lower,upper)

    #contours_tmp, hierarchy_tmp = cv2.findContours(tmp_crop,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #print str(idx_s) + " contained " + str(len(contours_tmp)) + "squares"

##Resize image
frame = resizeImage(frame, 0.25)
thresh = resizeImage(thresh, 0.5)
##Show Images 
cv2.imshow("thresh",thresh)
cv2.imshow("frame",frame)

cv2.waitKey(0)
