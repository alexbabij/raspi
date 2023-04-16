#! /usr/bin/python
#Test the display text function
import time
from display_text import *

counter = 0
while True:

    counter += 1
    string = "test,"+counter
    dispText(string,1)
    time.sleep(0.5)
