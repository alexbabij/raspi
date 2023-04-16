#! /usr/bin/python
#Test the display text function
import time
from display_text import *

counter = 0
while True:

    counter += 1
    string = "test,"+str(counter)
    dispText(string,counter*10)
    time.sleep(0.5)
    if counter >= 24:
        counter = 0

