#! /usr/bin/python
#The purpose of this is to wait to allow the user to begin collecting data until we have an adequate gps fix
from gps import *
import time
import subprocess
from gpiozero import Button

#We want to not allow the user to start taking data until we have an adequate fix, but we don't really want to terminate it partway 
#through a run if we end up losing the fix
modeDict = {'0':'unkown','1':'no fix','2':'2D fix','3':'3D fix'}

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 
goodFix = False  
startTime = time.time()
buttonEnabled = False

def whenPressed():
    global goodFix
    if buttonEnabled:
        goodFix = True

button = Button(21) #This is gpio 21, not pin 21
#Normally, .when_pressed only stays "active" while the script is being executed, so signal.pause() would need to be used to keep
#the button active. In our case, the while loop keeps the script running and the button active
button.when_pressed = whenPressed
#The way the pushbutton input works with gpiozero is it basically runs externally from this script in that it will run whenPressed
#outside of the while loop, meaning that even if the while loop sleeps for 1 second, the function whenPressed will execute immediately
#This implementation is still a little bit of a workaround, though, and we basically need to wait out an entire while loop cycle before
#it actually stops from the button press.

try:
 
     while goodFix == False:
                
        report = gpsd.next() #
        if report['class'] == 'TPV': 
        #This a lame way to select the correct json object since gpsd will return multiple different objects in repeating order
            mode = getattr(report,'mode','0')

            if int(mode) <= 1:
                print("Waiting for fix, status:",modeDict[mode], "("+round((time.time()-startTime),1)+")s")
                buttonEnabled = False
                
            elif (mode == '2') | (mode == '3'):
                print("Status:",modeDict[mode],"ready to start - push button to begin data collection")
                buttonEnabled = True
                startTime = time.time()
        
        time.sleep(1)                

         
    
except KeyError:
        pass #We would rather just skip if we cannot get good data rather than have our stuff error out
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nExiting.")
else:
    print("Running data collection\n")

subprocess.run(["python","collect_data.py"])