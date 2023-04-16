#! /usr/bin/python
#Test the display text function
import time
from display_text import *

counter = 0
while True:

    counter += 1

    dispText("test,",counter)
    time.sleep(1)
