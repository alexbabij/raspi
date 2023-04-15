#! /usr/bin/python
#pushbutton 2 
 
from signal import pause
from gpiozero import LED, Button
import time


flag = True

def on_press():
    global flag
    flag = False
    # do something when button is pressed
    print("Button pressed")

button = Button(2)

button.when_pressed = on_press

while flag:
    # do something else while button is not pressed
    print("Waiting for button press...")


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