#! /usr/bin/python
#The purpose of this is to wait to allow the user to begin collecting data until we have an adequate gps fix
from gps import *
import time
import subprocess


#We want to not allow the user to start taking data until we have an adequate fix, but we don't really want to terminate it partway 
#through a run if we end up losing the fix
modeDict = {'0':'unkown','1':'no fix','2':'2D fix','3':'3D fix'}

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 
goodFix = False  
startTime = time.time()

try:
 
     while goodFix == False:
                
        report = gpsd.next() #
        if report['class'] == 'TPV': 
        #This a lame way to select the correct json object since gpsd will return multiple different objects in repeating order
            mode = getattr(report,'mode','0')

            if int(mode) <= 1:
                print("Waiting for fix, status:",modeDict[mode], "("+round((time.time()-startTime),1)+")s")
            elif (mode == '2') | (mode == '3'):
                print(modeDict[mode],"ready to start")
                goodFix == True   
          

        time.sleep(1) 
    
except KeyError:
        pass #We would rather just skip if we cannot get good data rather than have our stuff error out
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nExiting.")
else:
    print("Running data collection\n")

subprocess.run(["python","collect_data.py"])