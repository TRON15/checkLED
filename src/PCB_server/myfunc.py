import numpy as np
import cv2
import RPi.GPIO as GPIO
import time
import subprocess
'''
--------------
match function
--------------
'''
error_limit = 1 # pixel
def equl_with_error(pos1, pos2):
    if(len(pos1) != len(pos2)):
        return 0
    else:
        for i in range(0,len(pos1)):
            if(abs(pos1[i]-pos2[i]) > error_limit):
                return 0
    return 1
# find elements in list1 but not in list2
def find_difference(list1,list2):
    difference = []
    for pos1 in list1:
        # flag - also in list2
        flag = 0
        for pos2 in list2:
            if(equl_with_error(pos1, pos2)):
                flag = 1
        if(flag == 0):
            to_be_add = []
            for i in range (0,len(pos1)):
                to_be_add.append(int(pos1[i]))
            difference.append(to_be_add)
    return difference

'''
---------------------------
Advanced settings interface
---------------------------
'''
def set_range(low, high):
    global exp_range
    exp_range = range(low, high)
    return exp_range[0], (exp_range[len(exp_range)-1]+1)
def get_range():
    return exp_range[0], (exp_range[len(exp_range)-1]+1)
def set_test_num(num):
    global test_num
    test_num = num
    return test_num
def get_test_num():
    return test_num
'''
----------------------------
find the postion of each led
----------------------------
'''
# range of exposure, change when using different comb leds
global exp_range
exp_range = range(1, 36)
# number of test each pattern
global test_num
test_num = 3
# area limit, change when using different comb leds
area_bound = 15
# area error limit
area_error_limit = 4
# findPos function
def findPos_frame(frame):
    # BGR to gary
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # binary
    binary_bound = 100
    ret, thresh = cv2.threshold(gray, binary_bound, 255, 0)
    image,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # get the position of leds
    leds = []
    areaS = []
    for cnt in contours:
        M = cv2.moments(cnt)
        if(abs(M['m00']-area_bound)<=area_error_limit):
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            area = cv2.contourArea(cnt)
            leds.append([cy,cx])
            areaS.append(area)
    # print(leds,areaS) # test only
    return leds, areaS
def findPos_cap(cap_num, pattern_num, show_flag = 1, cali_or_check = 0):
    # list to store num point
    leds_cap = []
    # sampleFrame to store
    sampleFrame = None
    # start video capture
    cap = cv2.VideoCapture(cap_num)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    for i in range(0, test_num):
        # leds_cap for each test
        _leds_cap = []
        for exposure in exp_range:
            print('exposure', exposure)
            # print('exposure:', exposure) # test only
            # set exposure
            subprocess_text = 'v4l2-ctl -d /dev/video{_cap_num} -c exposure_auto=1 -c exposure_auto_priority=0 -c exposure_absolute={_exposure}'
            subprocess_text = subprocess_text.format(_cap_num = cap_num, _exposure = exposure)
            # call subprocess
            subprocess.call(subprocess_text, shell = True)
            # read frame
            print('sub_success')
            ret, frame = cap.read()
            frame = frame[0:720, 170:1090]
            # findPos
            leds_frame, area = findPos_frame(frame)
            # get new leds postion
            differences = find_difference(leds_frame, leds_cap)
            # add new to the leds of the cap
            for different_leds in differences:
                _leds_cap.append(different_leds)
            # refresh leds_cap
            if (len(_leds_cap) > len(leds_cap)):
                leds_cap=_leds_cap
            # show the real time video stream
            patt_num_text = 'pattern: {_pattern_num}, exposure: {_exposure}, test times: {_test_time}'
            patt_num_text = patt_num_text.format(_pattern_num = pattern_num, _exposure = exposure, _test_time = (i+1))
            cv2.putText(frame, patt_num_text, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            for led in leds_cap:
                cv2.circle(frame, (led[1],led[0]), error_limit, (0,200,0), -1)
                text = '({posh},{posw})'
                text = text.format(posh = led[0], posw = led[1])
                cv2.putText(frame, text, (led[1],led[0]-16), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 255, 0), 1)
            sampleFrame = frame
            if(show_flag):
                cv2.imshow('frame',frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    if (cali_or_check == 1):
        frameName  = '/frame/pattern{ptNum}.png'
        frameName = frameName.format(ptNum = pattern_num)
        cv2.putText(sampleFrame, 'Standard', (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        cv2.imwrite(frameName, sampleFrame)
    elif (cali_or_check  == 2):
        frameName  = '/frame/check_pattern{ptNum}.png'
        frameName = frameName.format(ptNum = pattern_num)
        cv2.imwrite(frameName, sampleFrame)
    else:
        pass
    # When everything done, release the capture
    cap.release()
    # to show better close window by yourself
    return leds_cap, len(leds_cap)

'''
------------
io opeartion
------------
'''
# 11 IO -17,27,22,5,6,13,19,26,16,20,21
iolist = [17,27,22,5,6,13,19,26,16,20,21]
# send message to control
def send_message_1():
##    for i in range(0,5):
##        GPIO.output(26, GPIO.HIGH)
##        time.sleep(0.5)
##        GPIO.output(26, GPIO.LOW)
##        time.sleep(0.5)
##    GPIO.output(26, GPIO.LOW)

    GPIO.output(13, GPIO.LOW)
    GPIO.output(19, GPIO.HIGH)
    print('smf1')
def send_message_2():
##    for i in range(0,5):
##        GPIO.output(26, GPIO.HIGH)
##        time.sleep(0.3)
##        GPIO.output(26, GPIO.LOW)
##        time.sleep(0.3)
##    GPIO.output(26, GPIO.LOW)

    GPIO.output(19, GPIO.LOW)
    GPIO.output(13, GPIO.HIGH)
    print('smf2')
def send_message_3():
##    for i in range(0,5):
##        GPIO.output(26, GPIO.HIGH)
##        time.sleep(0.1)
##        GPIO.output(26, GPIO.LOW)
##        time.sleep(0.1)
##    GPIO.output(26, GPIO.LOW)

    GPIO.output(13, GPIO.LOW)
    GPIO.output(19, GPIO.HIGH)
    print('smf3')
def send_message_4():
##    for i in range(0,10):
##        GPIO.output(26, GPIO.HIGH)
##        time.sleep(0.5)
##    GPIO.output(26, GPIO.LOW)
    GPIO.output(19, GPIO.LOW)
    GPIO.output(13, GPIO.HIGH)
    print('smf4')
# list for the function to control
# ADD THE NAME OF NEW SEND MES FUNCTION TO THE LIST!!!
send_message = [send_message_1, send_message_2, send_message_3, send_message_4]
##def error_processing():
