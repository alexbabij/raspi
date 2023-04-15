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
#Basically, we want to refresh this faster than the update rate of our gps since the time to execute gpsd.next() will scale with 
#our refresh rate. In other words, even if our sleepinterval is 0.1s, but our frequency is 1s, the time to execute 1 cycle will be 
#close to 1 second because gpsd will wait to complete gpsd.next
#At the same time, though, gpsd will send multiple different json objects, only one of which will be the TPV report we want, so
#to be safe, we will just refresh much faster than we would be getting TPV reports

vehicle = config["current vehicle"]





#We want to not allow the user to start taking data until we have an adequate fix, but we don't really want to terminate it partway 
#through a run if we end up losing the fix

#This is our list that contains all time and velocity samples for the current run
gpsData = []
rollingGpsData = []
currentData = ['',float('nan')]
counter = 0
totCounter = counter + 1 #totCounter interrupts from the top of the loop, so we want to log our last chunk of data
#write our data to a file every 1 second 
samplesC = int(config["storage interval"]) * updateRate #Only whole second intervals are allowed otherwise this counter could be a decimal
totSamplesC = float(config["timeout"]) * updateRate #Basically a timeout in case we don't stop taking data (120 seconds)
#Should make a rolling estimation of acceleration to determine where data starts
gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 

from fileSave import *


filePath = ""
fileCreated = False
try:
 
     while True & (totCounter < totSamplesC):
        
        start = time.time()
        report = gpsd.next() #
        if report['class'] == 'TPV': 
        #This a lame way to select the correct json object since gpsd will return multiple different objects in repeating order
             
            if (math.isfinite(getattr(report,'speed',float('nan')))) & (getattr(report,'time','') !=''):
            #If the data is bad we just ignore it, the format for this is to return NaN for numbers and empty for strings: ''
            #Not sure how much an effect on performance this has

                currentData = [getattr(report,'time',''),getattr(report,'speed','nan')]
                
                #We should never get nan or an empty string since we check for it, but just in case, we don't want this to stop collecting data
                gpsData.append(currentData)
                rollingGpsData.append(currentData)
            print(currentData)
            
            
            
            end = time.time()
            elapsed = (end-start)
            print('\nTime/refresh',elapsed)

            if (counter >= samplesC):
                filePath, fileCreated = writeFile(vehicle,rollingGpsData,fileCreated,filePath)
                counter = 0
                print("Saved data:",rollingGpsData)
                rollingGpsData = []
                
            counter += 1
            totCounter += 1
            print(totCounter)

        time.sleep(sleepInterval) 
except KeyError:
        pass #We would rather just skip if we cannot get good data rather than have our stuff error out
except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nExiting.")
    filePath, fileCreated = writeFile(vehicle,rollingGpsData,fileCreated,filePath)
else:
    print(gpsData)


#Parsing the GPSD json:
