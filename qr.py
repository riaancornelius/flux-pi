import os
import cv2
import math
import numpy as np
import subprocess
import re


def scan_qr_code(_qr_name):
    result = None
    try:
        #result = subprocess.check_output(["C:\\Program Files (x86)\\ZBar\\bin\\zbarimg", "-q", "aa_cropped_1.png"])
        result = subprocess.check_output(["C:\\Program Files (x86)\\ZBar\\bin\\zbarimg", "-q", _qr_name])
    except:
        print "  Error while scanning potential QR Code: " + qr_name
        result = None
    return result


def get_id_from_qr_code_scan_result(possible_qr_id):
    p = re.compile("QR-Code:(.+)", re.IGNORECASE)
    match = p.match(possible_qr_id)
    if match:
        ticket_id = match.group(1)
        print ticket_id
        return ticket_id
        

##Resize with resize command
def resize_image(img0, ratio):
    dst = cv2.resize(img0, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_LINEAR)
    return dst


def process_contours(_contours, _hierarchy=None, _frame=None, draw_contours=1):
    squares = []
    for idx, contour in enumerate(_contours):
        moment = cv2.moments(contour)
        should_count = True
        if _hierarchy is not None and _hierarchy[0, idx, 3] > -1:
            should_count = False
            print "Hierarchy for " + str(idx) + " was: " + str(_hierarchy[0, idx, 3])
        if should_count is True and moment["m00"] > 1000:
            bounding_box = cv2.boundingRect(contour)
            orig_rect = cv2.minAreaRect(contour)
            rect = ((orig_rect[0][0], orig_rect[0][1]), (orig_rect[1][0], orig_rect[1][1]), orig_rect[2])
            (width, height) = (rect[1][0], rect[1][1])
            #print str(width)+" "+str(height)
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)
            if 0.8*width < height < 1.2*width:
                squares.append(bounding_box)
                if draw_contours == 1 and _frame is not None:
                    cv2.drawContours(_frame, [box], 0, (0, 0, 255), 4)
    return squares, _frame


##Take image with Raspberry Pi camera
#os.system("raspistill -w 2592 -h 1944 -ex verylong -o /home/pi/Desktop/flux-pi/image.jpg")

##Load image
#frame = cv2.imread('/home/pi/Desktop/flux-pi/image.jpg')
frame = cv2.imread('c:/Work/Entelect/DevDay022014/flux-pi/image.jpg')

##Run Threshold on image to make it black and white
ret, thresh = cv2.threshold(frame, 60, 255, cv2.THRESH_BINARY)

lower = np.array([0, 0, 0], np.uint8)
upper = np.array([10, 50, 50], np.uint8)
separated = cv2.inRange(thresh, lower, upper)

##Find outer squares using contours
contours, hierarchy = cv2.findContours(separated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
outerSquares, tmp = process_contours(contours, None, frame, 1)

#print "idx: " + str(idx)
print "Found squares to check: " + str(len(outerSquares))

probableQrCodes = []
for idx_s, square in enumerate(outerSquares):
    x, y, w, h = square
    x += 8
    y += 8
    w -= 16
    h -= 16
    tmp_crop = thresh[y:y+h, x:x+w]
    ret, thresh_tmp = cv2.threshold(tmp_crop, 50, 255, cv2.THRESH_BINARY)
    cv2.imwrite("aa_cropped_"+str(idx_s)+'.png', thresh_tmp)

    lower = np.array([0, 0, 0], np.uint8)
    upper = np.array([10, 50, 50], np.uint8)
    separated_tmp = cv2.inRange(thresh_tmp, lower, upper)

    contours_tmp, hierarchy_tmp = cv2.findContours(separated_tmp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    innerSquares, drawnFrame = process_contours(contours_tmp, hierarchy, thresh_tmp, 1)
    #cv2.imwrite("aa_marked_"+str(idx_s)+'.png', drawnFrame)
    #print str(idx_s) + " contained " + str(len(innerSquares)) + " squares"
    if len(innerSquares) >= 3:
        result = [tmp_crop, square]
        probableQrCodes.append(result)

print "Found possible QR codes: " + str(len(probableQrCodes))
print "First result length: " + str(len(probableQrCodes[0]))

qr_codes = []
for idx_qr, (tmp_qr, square) in enumerate(probableQrCodes):
    qr_name = "aa_qr_"+str(idx_qr)+'.png'
    cv2.imwrite(qr_name, tmp_qr)
    scan_result = get_id_from_qr_code_scan_result(scan_qr_code(qr_name))
    if scan_result is not None:
        qr_codes.append([scan_result, square])

for idx_qr, (ticket_id, location) in enumerate(qr_codes):
    x, y, w, h = location
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    #cv2.drawContours(frame, [[[x, y]], [[x+w, y+h]]], 0, (0, 0, 255), 4)



##Resize image
frame = resize_image(frame, 0.33)
thresh = resize_image(thresh, 0.33)
##Show Images 
#cv2.imshow("thresh", thresh)
cv2.imshow("frame", frame)

cv2.waitKey(0)
