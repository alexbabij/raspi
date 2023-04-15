#! /usr/bin/python
#pushbutton 2 
 
from signal import pause
from gpiozero import LED, Button
import time


button = Button(21)

state = False
switch = True
def go_blink():
    print("button pressed")

try:
    button.when_pressed = go_blink
    pause(2)

finally:
    print("finally done")
    pass

# #button.wait_for_press()
# def buttonPressTog():
#     global state
#     state = True


# def signalHandler(signum, frame):
    

# try:

#     while state == False:
#         if switch == True:
            
#             print("enabled")
#             switch = False
#             time.sleep(1)
#         else:
            
#             print("disabled")
#             switch = True
#             time.sleep(1)


# finally:
#     pass

# print("button pressed, script finished")