import os
import cv2
import cv
import math
import numpy as np
import subprocess
import re

def scanQrCode(qr_name):
    result = None
    try:
        #result = subprocess.check_output(["C:\\Program Files (x86)\\ZBar\\bin\\zbarimg", "-q", "aa_cropped_1.png"])
        result = subprocess.check_output(["C:\\Program Files (x86)\\ZBar\\bin\\zbarimg", "-q", qr_name])
    except:
        print "  Error while scanning potential QR Code: " + qr_name
        result = None
    return result

def getIdFromQrCodeScanResult(possible_qr_id):
    p = re.compile("QR-Code:(.+)", re.IGNORECASE);
    match = p.match(possible_qr_id)
    if match:
        print match.group(1)
        

##Resize with resize command
def resizeImage(img0, ratio):
    dst = cv2.resize(img, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_LINEAR)
    return dst

def processContours(contours, hierarchy = None, frame = None, draw_contours = 1):
    squares = []
    for idx, contour in enumerate(contours):
        moment = cv2.moments(contour)
        shouldCount = True
        if hierarchy != None and hierarchy[0, idx, 3] > -1:
            shouldCount = False
            print "Hierarchy for " + str(idx) + " was: " + str(hierarchy[0, idx, 3])
        if shouldCount == True and moment["m00"] > 1000:
            bounding_box = cv2.boundingRect(contour)
            orig_rect = cv2.minAreaRect(contour)
            rect = ((orig_rect[0][0], orig_rect[0][1]), (orig_rect[1][0], orig_rect[1][1]), orig_rect[2])
            (width,height)=(rect[1][0],rect[1][1])
            #print str(width)+" "+str(height)
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)
            if(height>0.8*width and height<1.2*width):
                squares.append(bounding_box)
                if draw_contours == 1 and frame != None:
                    cv2.drawContours(frame, [box], 0, (0, 0, 255), 4)
##    if draw_contours == 1 and frame != None:
##        cv2.imshow("frame", frame)
    return squares, frame

##Take image with Raspberry Pi camera
#os.system("raspistill -w 2592 -h 1944 -ex verylong -o /home/pi/Desktop/flux-pi/image.jpg")

##Load image
#img = cv2.imread("/home/pi/Desktop/flux-pi/image.jpg") 
#grey = cv2.imread("/home/pi/Desktop/flux-pi/image.jpg",0) #0 for grayscale

#frame=cv2.imread('/home/pi/Desktop/flux-pi/image.jpg')
frame=cv2.imread('c:/Work/Entelect/DevDay022014/flux-pi/image.jpg')
#img=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


#grey = cv2.imread("/home/pi/Desktop/flux-pi/image.jpg",0) #0 for grayscale
#img = cv2.GaussianBlur(frame, (1,1), 0)

##Run Threshold on image to make it black and white
ret, thresh = cv2.threshold(frame,50,255,cv2.THRESH_BINARY)

lower=np.array([0, 0, 0],np.uint8)
upper=np.array([10, 50, 50],np.uint8)
separated=cv2.inRange(thresh,lower,upper)

##Find outer squares using contours

contours,hierarchy=cv2.findContours(separated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
#contours,hierarchy=cv2.findContours(separated,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
#contours,hierarchy=cv2.findContours(separated,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
outerSquares, tmp = processContours(contours, None, frame)
##for idx, contour in enumerate(contours):
##    moment = cv2.moments(contour)
##    if moment["m00"] > 1000:
##        bounding_box = cv2.boundingRect(contour)
##        orig_rect = cv2.minAreaRect(contour)
##        rect = ((orig_rect[0][0], orig_rect[0][1]), (orig_rect[1][0], orig_rect[1][1]), orig_rect[2])
##        (width,height)=(rect[1][0],rect[1][1])
##        #print str(width)+" "+str(height)
##        box = cv2.cv.BoxPoints(rect)
##        box = np.int0(box)
##        if(height>0.8*width and height<1.2*width):
##            squares.append(bounding_box)
##            cv2.drawContours(frame,[box], 0, (0, 0, 255), 4)

#print "idx: " + str(idx)
print "Found squares to check: " + str(len(outerSquares))

probableQrCodes = []
for idx_s, square in enumerate(outerSquares):
    x,y,w,h = square
    x += 8
    y += 8
    w -= 16
    h -= 16
    tmp_crop = thresh[y:y+h,x:x+w]
    ret, thresh_tmp = cv2.threshold(tmp_crop,50,255,cv2.THRESH_BINARY)
    cv2.imwrite("aa_cropped_"+str(idx_s)+'.png', thresh_tmp)

    lower=np.array([0, 0, 0],np.uint8)
    upper=np.array([10, 50, 50],np.uint8)
    separated_tmp = cv2.inRange(thresh_tmp,lower,upper)

    contours_tmp, hierarchy_tmp = cv2.findContours(separated_tmp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    innerSquares, drawnFrame = processContours(contours_tmp, hierarchy, thresh_tmp, 1)
    #cv2.imwrite("aa_marked_"+str(idx_s)+'.png', drawnFrame)
    #print str(idx_s) + " contained " + str(len(innerSquares)) + " squares"
    if len(innerSquares) >= 3:
        probableQrCodes.append(tmp_crop)

print "Found possible QR codes: " + str(len(probableQrCodes))

for idx_qr, tmp_qr in enumerate(probableQrCodes):
    qr_name = "aa_qr_"+str(idx_qr)+'.png'
    cv2.imwrite(qr_name, tmp_qr)
    getIdFromQrCodeScanResult(scanQrCode(qr_name))

##Resize image
frame = resizeImage(frame, 0.33)
thresh = resizeImage(thresh, 0.33)
##Show Images 
#cv2.imshow("thresh",thresh)
#cv2.imshow("frame",frame)

cornerMap = cv.CreateMat(image.height, image.width, cv.CV_32FC1)
# OpenCV corner detection
cv.CornerHarris(image,cornerMap,3)

for y in range(0, image.height):
 for x in range(0, image.width):
  harris = cv.Get2D(cornerMap, y, x) # get the x,y value
  # check the corner detector response
  if harris[0] > 10e-06:
   # draw a small circle on the original image
   cv.Circle(imcolor,(x,y),2,cv.RGB(155, 0, 25))

cv.NamedWindow('Harris', cv.CV_WINDOW_AUTOSIZE)
cv.ShowImage('Harris', imcolor) # show the image
cv.SaveImage('harris.jpg', imcolor)


cv2.waitKey(0)
