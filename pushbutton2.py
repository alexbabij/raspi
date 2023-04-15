#! /usr/bin/python
#pushbutton 2 
 
from signal import pause
from gpiozero import LED, Button


button = Button(21)

button.wait_for_press()

print("button pressed, script finished")