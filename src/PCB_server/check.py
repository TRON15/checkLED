import cv2
import numpy as np
import PCBconfig as pcb
import myfunc
from myfunc import send_message
from myfunc import iolist
from myfunc import findPos_cap
from myfunc import equl_with_error
from myfunc import find_difference
import RPi.GPIO as GPIO
# error list to store errors info
error_list = []
# start GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(iolist,GPIO.OUT)
# check length of send_message functions and ledlist
if(len(send_message)==len(pcb.ledlist)):
    # big FOR to send patterns
    for smf in send_message:
        smf()
        print('pattren ', (send_message.index(smf)+1),' processing...')
        pos, pointNum = findPos_cap(0,(send_message.index(smf)+1))
        lost = find_difference(pcb.ledlist[send_message.index(smf)], pos)
        new = find_difference(pos, pcb.ledlist[send_message.index(smf)])
        if((lost != []) or (new != [])):
            error_list.append([(send_message.index(smf)+1), lost, new])
    # error analsy
    if (error_list == []):
        print("Qualified")
    else:
        for error in error_list:
            print('Please cheak the leds in those postions!!!')
            print('In pattern ', error[0], ':')
            print('we lost leds in ', error[1], 'and lighting unexpected leds in ', error[2])
else:
    print('length of ledlist dont match the length of patteens!!! please check them!')
# When everything done, clean up GPIO
cv2.destroyAllWindows()
GPIO.cleanup()
