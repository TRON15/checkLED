from __future__ import print_function
import sys,os 
import cv2
import numpy as np
import myfunc
import RPi.GPIO as GPIO
from myfunc import findPos_cap
from myfunc import send_message
from myfunc import iolist
# tips for user
print('DO NOT CLOSE! I am working...')
# start GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(iolist,GPIO.OUT)
# list of leds
ledlist = []
# big FOR to send patterns
for smf in send_message:
    print('----------------')
    print('pattern',(send_message.index(smf)+1),':')
    smf()
    pos, pointNum = findPos_cap(0,(send_message.index(smf)+1))
    ledlist.append(pos)
    for i in range(0,pointNum):
        print('point', (i+1), ':', 'h-', int(pos[i][0]), 'w-', int(pos[i][1]))
    print('----------------')
# store it in PCBconfig.py
f=open('PCBconfig.py','r+')  
flist=f.readlines()
config_str = 'ledlist = {_ledlist}\n'
config_str = config_str.format(_ledlist=ledlist)
flist[2] = config_str  
f=open('PCBconfig.py','w+')  
f.writelines(flist) 
f.close()
print('postion infomation has stored in PCBconfig.py')
# When everything done, clean up GPIO and windows
cv2.destroyAllWindows()
GPIO.cleanup()
