#! /usr/bin/python
#Test the display text function
import time
from display_text import *

timee = 0
counter = 0
startt = time.time()
rounding = 0
location = 0
frameC = 0
loDict = {1: "northwest", 2: "southwest", 3: "southeast", 4: "northeast"}
dispBackground([0,0,0])
while True:

    frameC += 1
    counter += 1
    timee += 0.1
    rounding += 1
    location += 1
    truet = time.time()-startt
    string = "test,"+str(round(timee,1))+"\n"+str(round(truet,rounding)+"\nFrame: "+str(frameC))
    dispText(string,loDict[location],fontColor=[205,153,51,255])
    time.sleep(0.1)
    if counter >= 24:
        counter = 0
    if rounding >= 4:
        rounding = 1
    if location >= 4:
        location = 0
   