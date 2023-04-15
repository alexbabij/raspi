#! /usr/bin/python
#Running this file will collect gps data at the specified interval 
from gps import *
import time
import math

#Configure gps settings including update rate
with open('configDevice.txt') as mycfgfile:
    config = mycfgfile.read().splitlines() #Read in each line as a list i.e. [a:1, b:2]
    config = dict([eachLine.split(":") for eachLine in config]) #Split by ":" and turn into dict
updateRate = int(config["updateRate"])
sleepInterval = 1/(updateRate*10) #Maybe tweak this depending on performance
#gpsd is weird, and while it should be waiting to return a NEW report every time we query it, it doesn't and will return around 4 TPV
#reports, regardless of how long we wait to query it again in our loop, idk. The above works and doesn't cause it to lag or take longer
#than the interval it is timing to run the entire function, unlike using something like:1/(updateRate*2)

vehicle = config["current vehicle"]





#We want to not allow the user to start taking data until we have an adequate fix, but we don't really want to terminate it partway 
#through a run if we end up losing the fix

#This is our list that contains all time and velocity samples for the current run
gpsData = []
rollingGpsData = []
currentData = ['',float('nan')]
counter = 0
#write our data to a file every 1 second 
samplesC = int(config["storage interval"]) * updateRate #Only whole second intervals are allowed otherwise this counter could be a decimal
totSamplesC = float(config["timeout"]) + time.time() 
#Basically a timeout in case we don't stop taking data within timeout period


#Should make a rolling estimation of acceleration to determine where data starts ########################

totstart = time.time()
#we do our timeout using time.time() instead of counting the successful writes, because then it will truly be timing out based on time
#instead of timing out based on writes, meaning if we have a period of unsuccessful writes/data it will still timeout normally

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 

from fileSave import *

start = time.time()
filePath = ""
fileCreated = False
try:
 
     while True & (time.time() < totSamplesC):
        
        
        report = gpsd.next() #
        if report['class'] == 'TPV': 
        #This a lame way to select the correct json object since gpsd will return multiple different objects in repeating order
             
            if (math.isfinite(getattr(report,'speed',float('nan')))) & (getattr(report,'time','') !=''):
            #If the data is bad we just ignore it, the format for this is to return NaN for numbers and empty for strings: ''
            #Not sure how much an effect on performance this has

                currentData = [getattr(report,'time',''),getattr(report,'speed','nan')]
                #We should never get nan or an empty string since we check for it, but just in case, we don't want this to stop collecting data
                #We are capable of getting duplicate results, so we filter them out

                if len(gpsData) == 0:
                    gpsData.append(currentData)
                    rollingGpsData.append(currentData)
                    counter += 1 #We save our file after 5 SUCCESSFUL readings
                    print("Time since start:",time.time()-totstart)
                    print(currentData)

                elif gpsData[-1][0] != currentData[0]:
                    gpsData.append(currentData)
                    rollingGpsData.append(currentData)
                    counter += 1
                    print("Time since start:",time.time()-totstart)
                    print(currentData)          
            
            end = time.time()
            elapsed = (end-start)
            start = time.time()
            print('\nTime/refresh',elapsed)

            if (counter >= samplesC):
                filePath, fileCreated = writeFile(vehicle,rollingGpsData,fileCreated,filePath)
                counter = 0
                print("Saved data:",rollingGpsData)
                rollingGpsData = []
                
            
          
        time.sleep(sleepInterval) 
    
except KeyError:
        pass #We would rather just skip if we cannot get good data rather than have our stuff error out
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nExiting.")
    filePath, fileCreated = writeFile(vehicle,rollingGpsData,fileCreated,filePath)
else:
    if not counter == 0:
        filePath, fileCreated = writeFile(vehicle,rollingGpsData,fileCreated,filePath)
        print("Saved data:",rollingGpsData)
        print("Finished collecting data")
        #Write the rest of the data when we exit the while loop
    print(gpsData)
    totend = time.time() - totstart
    print("\nCompleted in:",totend)



#Parsing the GPSD json:
