import os
import cv2
import math
import numpy as np
import subprocess
import re
import time
from jira import JiraTicketSearch
from jira import JiraTicket
from datetime import datetime

STATUS_UNKNOWN = -1
STATUS_READY = 0
STATUS_IN_PROGRESS = 1
STATUS_DONE = 2

ZBAR_PATH = "C:\\Program Files (x86)\\ZBar\\bin\\zbarimg"

#OUTPUT_PATH = "/home/pi/Desktop/flux-pi/"
OUTPUT_PATH = 'c:/Work/Entelect/DevDay022014/flux-pi/'
IMAGE_NAME = 'image'
IMAGE_EXT = '.jpg'


def status_name(_status):
    if _status == STATUS_READY:
        return "To Do"
    elif _status == STATUS_IN_PROGRESS:
        return "In Progress"
    elif _status == STATUS_DONE:
        return "Done"
    else:
        return "To Do"


def scan_qr_code(_qr_name):
    result = None
    try:
        result = subprocess.check_output([ZBAR_PATH, "-q", _qr_name])
    except:
        print "  Error while scanning potential QR Code: " + qr_name
        result = None
    return result


def get_id_from_qr_code_scan_result(possible_qr_id):
    print "possible QR Code found: " + possible_qr_id
    p = re.compile("QR-Code:(.+)", re.IGNORECASE)
    match = p.match(possible_qr_id)
    if match:
        return match.group(1).strip()
        

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


def display_image(img):
    screen_res = 1280, 720
    scale_width = screen_res[0] / img.shape[1]
    scale_height = screen_res[1] / img.shape[0]
    scale = min(scale_width, scale_height)
    window_width = int(img.shape[1] * scale)
    window_height = int(img.shape[0] * scale)

    cv2.resizeWindow('dst_rt', window_width, window_height)

    cv2.imshow('dst_rt', img)


def get_status_from_ypos(_lane_height, _square):
    xpos, ypos, width, height = _square
    if 0 < ypos < _lane_height:
        return STATUS_READY
    if _lane_height < ypos < _lane_height*2:
        return STATUS_IN_PROGRESS
    if _lane_height * 2 < ypos:
        return STATUS_DONE

def main():
    print 'Run started...'
    loop_run_count = 1
    history = {}
    while True:
        print "--- Starting main loop. Run: " + str(loop_run_count) + " (" + datetime.now().strftime('%H:%M:%S') + ")"

        ##Take image with Raspberry Pi camera
        #os.system("raspistill -w 2592 -h 1944 -ex verylong -o " + OUTPUT_PATH + IMAGE_NAME + IMAGE_EXT)

        ##Load image
        #frame = cv2.imread(OUTPUT_PATH)
        frame = cv2.imread(OUTPUT_PATH + IMAGE_NAME + str(loop_run_count) + IMAGE_EXT)
        if frame is None:
            frame = cv2.imread(OUTPUT_PATH + IMAGE_NAME + IMAGE_EXT)
        board_height, width, depth = frame.shape
        lane_height = board_height/3

        ##Run Threshold on image to make it black and white
        ret, thresh = cv2.threshold(frame, 60, 255, cv2.THRESH_BINARY)

        lower = np.array([0, 0, 0], np.uint8)
        upper = np.array([10, 50, 50], np.uint8)
        separated = cv2.inRange(thresh, lower, upper)

        ##Find outer squares using contours
        contours, hierarchy = cv2.findContours(separated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        outerSquares, tmp = process_contours(contours, None, frame, 0)

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

        qr_codes = []
        qr_codes_with_pos = []
        statuses = {}
        for idx_qr, (tmp_qr, square) in enumerate(probableQrCodes):
            qr_name = "aa_qr_"+str(idx_qr)+'.png'
            cv2.imwrite(qr_name, tmp_qr)
            scan_result = get_id_from_qr_code_scan_result(scan_qr_code(qr_name))
            if scan_result is not None:
                qr_codes.append(scan_result)
                qr_codes_with_pos.append([scan_result, square])
                ticket_status = get_status_from_ypos(lane_height, square)
                statuses[scan_result] = status_name(ticket_status)
                if scan_result not in history:
                    ticket_history = []
                    previous_status = -1
                else:
                    ticket_history = history[scan_result]
                    previous_status = ticket_history[-1]
                if previous_status != ticket_status:
                    ticket_history.append(ticket_status)
                    history[scan_result] = ticket_history

        print "Confirmed QR codes: " + str(len(qr_codes))
        print str(statuses)

        ## Fetch statuses from JIRA:
        search = JiraTicketSearch(qr_codes)
        issues = search.fetch()

        ## Check status against board position
        for issue in issues:
            if issue.is_status(statuses[issue.key]) != True:
                updated = JiraTicket(issue.key, statuses[issue.key]).update_online()
                print 'Updated ' + issue.key + ': ' + str(updated)

        cv2.waitKey(0)

        loop_run_count += 1
        print 'Run complete. Going to sleep now'
        time.sleep(60)  # Delay for 1 minute (60 seconds)

"""
        font = cv2.FONT_HERSHEY_SIMPLEX

        for idx_qr, (ticket_id, location) in enumerate(qr_codes_with_pos):
            x, y, w, h = location
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 180, 180), 5)
            #cv2.putText(img,'OpenCV',(10,500), font, 4,(255,255,255),2,cv2.LINE_AA)
            print ticket_id
            cv2.putText(frame, ticket_id, (x, y-5), font, 1.5, (100, 255, 100), 3)
            for idx_history, ticket_history in enumerate(history[ticket_id]):
                cv2.putText(frame, "->" + status_name(ticket_history), (x-200, y+(35*(idx_history+1))), font, 1, (50, 50, 255), 3)

        ##Resize image
        frame = resize_image(frame, 0.42)
        thresh = resize_image(thresh, 0.25)
        ##Show Images
        cv2.imshow("thresh", thresh)
        cv2.imshow("frame", frame)
        #display_image(frame)

        cv2.waitKey(0)

        loop_run_count += 1
        time.sleep(1)  # Delay for 1 minute (60 seconds)
        cv2.destroyAllWindows()
"""

if __name__ == "__main__":
    main()
