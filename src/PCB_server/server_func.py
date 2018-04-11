import sys,os 
import cv2
import numpy as np
import myfunc
from bottle import route,request,response,static_file
from myfunc import *
from PIL import Image, ImageDraw
import RPi.GPIO as GPIO

@route('/server_func/GPIO_start', method = 'POST')
def GPIO_start():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(iolist,GPIO.OUT)
    res = {'result': 'GPIO setup'}
    response.content_type = 'application/json'
    return res

@route('/server_func/GPIO_clean', method = 'POST')
def GPIO_clean():
    GPIO.cleanup()
    res = {'result': 'GPIO clean up'}
    response.content_type = 'application/json'
    return res

@route('/server_func/look', method = 'POST')
def look():   
    smf_num = request.json[u'smf_num']
    cali_or_check = request.json[u'cali_or_check']
    send_message[smf_num]() 
    pos, pointNum = findPos_cap(0,(smf_num+1), 0, cali_or_check)
    res = {'pos': pos, 'pointNum': pointNum}
    response.content_type = 'application/json'
    return res

@route('/server_func/st_ledlist', method = 'POST')
def st_ledlist():
    f = open('/home/pi/PCB_test/PCBconfig.py', 'r+')
    flist=f.readlines()
    f.close()
    led_str = flist[2]
    led_str = led_str[10:]
    ledlist = eval(led_str)
    res = {'st_ledlist': ledlist}
    response.content_type = 'application/json'
    return res

@route('/server_func/smf_len', method = 'POST')
def smf_len():
    res = {'smf_len': len(send_message)}
    response.content_type = 'application/json'
    return res 

@route('/server_func/upload_new_ledlist', method = 'POST')
def upload_new_ledlist():
    new_ledlist = request.json[u'new_ledlist']
    f = open('/home/pi/PCB_test/PCBconfig.py', 'r+')
    flist=f.readlines()
    config_str = 'ledlist = {_ledlist}\n'
    config_str = config_str.format(_ledlist = new_ledlist)
    flist[2] = config_str
    f=open('/home/pi/PCB_test/PCBconfig.py','w+')
    f.writelines(flist) 
    f.close()
    res = {'result': 'Upload done'}
    response.content_type = 'application/json'
    return res

@route('/server_func/get_frame', method = 'POST')
def get_frame():
    smf_num = request.json[u'smf_num']
    cali_or_check = request.json[u'cali_or_check']
    img = None
    frameName = None
    if(cali_or_check == 1):
        frameName = '/frame/pattern{ptNum}.png'
        frameName = frameName.format(ptNum = smf_num+1)
        img = open(frameName).read().encode('base64')
    elif(cali_or_check == 2):
        frameName = '/frame/check_pattern{ptNum}.png'
        frameName = frameName.format(ptNum = smf_num+1)
        img = open(frameName).read().encode('base64')
    else:
        pass
    res = {'frame': img}
    response.content_type = 'application/json'
    return res

@route('/server_func/get_ads', method = 'POST')
def get_ads():
    ads_num = request.json[u'ads_num']
    res = None
    if (ads_num == 0):
        low, high = get_range()
        res = {'low':low, 'high':high}
    elif (ads_num == 1):
        test_num = get_test_num()
        res = {'test_num':test_num}
    else:
        pass
    response.content_type = 'application/json'
    return res

@route('/server_func/set_ads', method = 'POST')
def set_ads():
    ads_num = request.json[u'ads_num']
    res = None
    if (ads_num == 0):
        neo_low = request.json[u'neo_low']
        neo_high = request.json[u'neo_high']
        low, high = set_range(neo_low, neo_high)
        print(low, high)
        res = {'low':low, 'high':high}
    elif (ads_num == 1):
        neo_test_num = request.json[u'neo_test_num']
        test_num = set_test_num(neo_test_num)
        res = {'test_num': test_num}
    else:
        pass
    response.content_type = 'application/json'
    return res
    
