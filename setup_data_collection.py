#! /usr/bin/python
#The purpose of this is to wait to allow the user to begin collecting data until we have an adequate gps fix
from gps import *
import time
import threading as tr
from gpiozero import Button
from display_text import *
#We want to not allow the user to start taking data until we have an adequate fix, but we don't really want to terminate it partway 
#through a run if we end up losing the fix


gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 
#This is how we get data from gpsd. using gpsd.next() will read the latest item in its buffer. This data is a json string
#that contains the information it got from the NMEA strings of the gps. We need to read this constantly, or else it will start
#to fill up and either provide old data, or overflow and stop working. 
goodFix = False  
startTime = time.time()
buttonEnabled = False

class gpsDataT(tr.Thread):
    def __init__(self):
        super().__init__()
        self.running = True    
        self.report = []

    def run(self):
        t1 = time.time()
        while self.running:
            self.report = gpsd.next()
            time.sleep(0.02)
            #print('elapsed',time.time()-t1) #DEBUG
            t1 = time.time()


def whenPressed():
    global goodFix
    if buttonEnabled:
        print("button Pressed")
        goodFix = True

button = Button(21) #This is gpio 21, not pin 21
#Normally, .when_pressed only stays "active" while the script is being executed, so signal.pause() would need to be used to keep
#the button active. In our case, the while loop keeps the script running and the button active
button.when_pressed = whenPressed
#The way the pushbutton input works with gpiozero is it basically runs externally from this script in that it will run whenPressed
#outside of the while loop, meaning that even if the while loop sleeps for 1 second, the function whenPressed will execute immediately
#This implementation is still a little bit of a workaround, though, and we basically need to wait out an entire while loop cycle before
#it actually stops from the button press.


gpsThread = gpsDataT() #We use this so we dont have to print out super fast
gpsThread.start()

# class buttonT(tr.Thread):
#     def __init__(self):
#         super().__init__()
#         self.running = True 

try:
    print("Waiting for data")
    time.sleep(2.0)
    while goodFix == False: #& self.running:
        #print("running")        
        print('goodFix',goodFix)
        #print(report) 
        prevString = ""
        
        if gpsThread.report['class'] == 'SKY': 
        #This a lame way to select the correct json object since gpsd will return multiple different objects in repeating order
            usedSats = getattr(gpsThread.report,'uSat',-1)
            #print('uSat:',usedSats) #DEBUG
            #print('report',gpsDataT.report)#DEBUG
            #print("mode:"+str(getattr(report,'mode',0))) #debug
            

            if usedSats == -1:
                print("parsing error")

                string = "parsing error"
                backgroundColor = [255,0,0] #Red
                fontColor = [0,0,0,255] #Black
                dispText(string,textLoc='center',fontColor=fontColor,FONTSIZE=15,backColor=backgroundColor)

                
            elif usedSats < 6:

                newString = str(int(usedSats))+"/6 sats"+" ("+str(round((time.time()-startTime),1))+")s"
                # if len(prevString)>len(newString):
                #     padding = " " * (len(prevString) + 1) #blank character for overwriting varying length string with carriage return
                # else:
                #     padding = ""
                # print(f"{newString}{padding}\r",end="") #fstring format, end="" prevents newline being made
                #print("1")
                # prevString = newString
                print(newString)
                string = newString
                backgroundColor = [255,255,0] #Yellow
                fontColor = [0,0,0,255] #Black
                dispText(string,textLoc='center',fontColor=fontColor,FONTSIZE=15,backColor=backgroundColor)
                buttonEnabled = False
                
                
            elif (usedSats >=6):

                newString = str(int(usedSats))+" sats: ready to start - push button to initialize data collection"
                # if len(prevString)>len(newString):
                #     padding = " " * (len(prevString) + 1) #blank character for overwriting varying length string with carriage return
                # else:
                #     padding = ""
                # print(f"{newString}{padding}\r",end="")
                # prevString = newString
                print(newString)
                buttonEnabled = True
                backgroundColor = [0,255,0] #Green
                fontColor = [0,0,0,255] #Black
                string = str(int(usedSats))+" sats"+"\nReady"+"\nPush Button"+"\nTo Start"
                dispText(string,textLoc='center',fontColor=fontColor,FONTSIZE=15,backColor=backgroundColor)
                startTime = time.time()
        
        time.sleep(0.5)

         
    
except KeyError:
        print("keyerror")
        pass #We would rather just skip if we cannot get good data rather than have our stuff error out
        
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    gpsThread.running=False
    gpsThread.join()
    print("\nExiting.")
else:
    gpsThread.running=False
    gpsThread.join()
    backgroundColor = [0,255,0] #Green
    fontColor = [0,0,0,255] #Black
    string = "Starting data\ncollection"
    dispText(string,textLoc='center',fontColor=fontColor,FONTSIZE=15,backColor=backgroundColor)
    print("Running data collection\n")



button.close() #release the button so we can use it in collect_gpsdata
#we need to release buttons because the gpiozero library does buttons at a fairly low level, and the process actually
#monitoring the button is kind of its own thing/thread/process
print("end")
#subprocess.run(["python","collect_data.py"])