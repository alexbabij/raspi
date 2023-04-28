#! /usr/bin/python
#The purpose of this is to wait to allow the user to begin collecting data until we have an adequate gps fix
from gps import *
import time
import subprocess
from gpiozero import Button

#We want to not allow the user to start taking data until we have an adequate fix, but we don't really want to terminate it partway 
#through a run if we end up losing the fix


gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 
goodFix = False  
startTime = time.time()
buttonEnabled = False

def whenPressed():
    global goodFix
    if buttonEnabled:
        print("button Pressed")
        #goodFix = True

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
        #print("running")        
        report = gpsd.next()
        #print(report) 
        prevString = ""
        
        if report['class'] == 'SKY': 
        #This a lame way to select the correct json object since gpsd will return multiple different objects in repeating order
            usedSats = getattr(report,'uSat',-1)
            #print('uSat:',usedSats) #DEBUG
            #print('report',report)#DEBUG
            #print("mode:"+str(getattr(report,'mode',0))) #debug
            

            if usedSats == -1:
                print("parsing error")
            elif usedSats <= 1:

                newString = str(int(usedSats))+"/6 sats"+" ("+str(round((time.time()-startTime),1))+")s"
                # if len(prevString)>len(newString):
                #     padding = " " * (len(prevString) + 1) #blank character for overwriting varying length string with carriage return
                # else:
                #     padding = ""
                # print(f"{newString}{padding}\r",end="") #fstring format, end="" prevents newline being made
                #print("1")
                # prevString = newString
                print(newString)
                buttonEnabled = False
                
                
            elif (usedSats >=6):

                newString = str(int(usedSats))+" sats ready to start - push button to begin data collection"
                # if len(prevString)>len(newString):
                #     padding = " " * (len(prevString) + 1) #blank character for overwriting varying length string with carriage return
                # else:
                #     padding = ""
                # print(f"{newString}{padding}\r",end="")
                # prevString = newString
                print(newString)
                buttonEnabled = True
                startTime = time.time()
        
        time.sleep(0.5)                

         
    
except KeyError:
        print("keyerror")
        pass #We would rather just skip if we cannot get good data rather than have our stuff error out
        
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nExiting.")
else:
    print("Running data collection\n")

print("end")
#subprocess.run(["python","collect_data.py"])