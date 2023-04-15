#! /usr/bin/python
#Pushbutton 
from signal import pause
from gpiozero import LED, Button

blink_on = False

def go_blink():
    global blink_on
    print("button pressed")
    if blink_on:
        led.off()
    else:
        led.blink(0.5,0.5)
    blink_on = not blink_on

button = Button(21)
led = LED(26)

try:
    button.when_pressed = go_blink
    pause()
finally:
    pass