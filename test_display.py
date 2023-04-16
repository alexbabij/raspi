#! /usr/bin/python
#Test the display text function
import time
from display_text import *

timee = 0
counter = 0
startt = time.time()
rounding = 0
while True:

    counter += 1
    timee += 0.1
    truet = time.time()-startt
    string = "test,"+str(round(timee,1))+" "+str(round(truet,rounding))
    dispText(string,"northwest")
    time.sleep(0.1)
    if counter >= 24:
        counter = 0
    if rounding >= 4:
        rounding = 1

