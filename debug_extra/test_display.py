#! /usr/bin/python
#Test the display text function
import time
from test_display_text import *

timee = 0
counter = 0
startt = time.time()
rounding = 0
location = 0
frameC = 0
loDict = {1: "northwest", 2: "southwest", 3: "southeast", 4: "northeast"}
dispBackground([0,0,0])
dispText("Startup","center",[255,255,255,255],25)
time.sleep(2)
while True:

    frameC += 1
    counter += 1
    timee += 0.1
    rounding += 1
    location += 1
    truet = time.time()-startt
    #location = 1
    string = "test,"+str(round(timee,1))+"\n"+str(round(truet,rounding))+"\nFrame: "+str(frameC)
    string += "\ntest"
    dispText(string,loDict[location],[205,153,51,255])
    time.sleep(0.05)
    if counter >= 24:
        counter = 0
    if rounding >= 4:
        rounding = 1
    if location >= 4:
        location = 0
   