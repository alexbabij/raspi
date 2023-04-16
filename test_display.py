#! /usr/bin/python
#Test the display text function
import time
from display_text import *

timee = 0
counter = 0
startt = time.time()
while True:

    counter += 1
    timee += 0.1
    truet = time.time()-startt
    string = "test,"+str(round(timee,1))+" "+str(round(truet),2)
    dispText(string,counter*10)
    time.sleep(0.1)
    if counter >= 24:
        counter = 0

