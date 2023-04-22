#! /usr/bin/python
#Running this file will collect gps data at the specified interval 
from gps import *
import os
import sys
import time
import math
import subprocess
import threading as tr #we don technically need this since threading gets imported in madgwick_filters





#Configure gps settings including update rate
with open('configDevice.txt') as mycfgfile:
    config = mycfgfile.read().splitlines() #Read in each line as a list i.e. [a:1, b:2]
    config = dict([eachLine.split(":") for eachLine in config]) #Split by ":" and turn into dict
updateRate = int(config["updateRate"])
sleepInterval = 1/(updateRate*10) #Maybe tweak this depending on performance
#gpsd is weird, and while it should be waiting to return a NEW report every time we query it, it doesn't and will return around 4 TPV
#reports, regardless of how long we wait to query it again in our loop, idk. The above works and doesn't cause it to lag or take longer
#than the interval it is timing to run the entire function, unlike using something like:1/(updateRate*2)

#The speed reading that comes out of gpsd is in m/s, this dictionary stores the conversion factor from m/s to [key]
conversionDict = {"mph": 2.2369362912, "kph": 3.6}
vehicle = config["current vehicle"]
cutoffSpeed = float(config["max speed"])/conversionDict[config["units"]]
maxSpeed = False #Set to true upon reaching our configured cutoff speed, ends the while loop and data collection


#This is our list that contains all time and velocity samples for the current run
#gpsData = []
#rollingGpsData = []
#currentData = ['',float('nan'),0.0,0.0]
#counter = 0
# #write our data to a file every 1 second 
# samplesC = int(config["storage interval"]) * updateRate #Only whole second intervals are allowed otherwise this counter could be a decimal
# totSamplesC = float(config["timeout"]) + time.time() 
# #Basically a timeout in case we don't stop taking data within timeout period


#we do our timeout using time.time() instead of counting the successful writes, because then it will truly be timing out based on time
#instead of timing out based on writes, meaning if we have a period of unsuccessful writes/data it will still timeout normally


#accDataMag = 0.0

sys.path.append(os.path.join(os.path.dirname(__file__), 'accelerometer'))
#from collect_accel_madgwick import *
from accelerometer.collect_accel_madgwick import *


from fileSave import *

class gpsThr(tr.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        #self.rollingGpsData = []
        
        


    def run(self):
        #this function definition of run(self) is a special method from threading. this function will automatically run when .start() is used 
        try:
            gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
            start = time.time()
            #write our data to a file every 1 second 
            samplesC = int(config["storage interval"]) * updateRate #Only whole second intervals are allowed otherwise this counter could be a decimal
            totSamplesC = float(config["timeout"]) + time.time() 
            #Basically a timeout in case we don't stop taking data within timeout period
            filePath = ""
            fileCreated = False
            totstart = time.time()
            gpsData = []
            rollingGpsData = []
            counter = 0
            print("gps rec started")
            while (self.running == True) & (time.time() < totSamplesC):
                
                
                report = gpsd.next()
                if report['class'] == 'TPV': 
                #This a lame way to select the correct json object since gpsd will return multiple different objects in repeating order
                    
                    if (math.isfinite(getattr(report,'speed',float('nan')))) & (getattr(report,'time','') !=''):
                    #If the data is bad we just ignore it, the format for this is to return NaN for numbers and empty for strings: ''
                    #Not sure how much an effect on performance this has
                        
                        #We record gps time, velocity, and time offset since starting script measured by the pi
                        currentData = [getattr(report,'time',''),getattr(report,'speed','nan'),(totstart-time.time()),0.0]
                        #We should never get nan or an empty string since we check for it, but just in case, we don't want this to stop collecting data
                        #We are capable of getting duplicate results, so we filter them out

                        #we want to have the acceleration value locked for as little time as possible
                        with accLock:
                            currentData[3] = accDataMag[0]
                            print("accDataMag",accDataMag[0])

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
                    #print('\nTime/refresh',elapsed)

                    if (counter >= samplesC):
                        filePath, fileCreated = writeFile(vehicle,rollingGpsData,fileCreated,filePath)
                        counter = 0
                        print("Saved data:",rollingGpsData)
                        rollingGpsData = []
                        
                    if gpsData[-1][1] >= (cutoffSpeed*1.1):
                        self.running = False
                    
                    if gpsData[-1][1] >= (cutoffSpeed):
                        self.running = False
                        #totSamplesC = time.time() + 1 

                    #Record data up until reaching slightly past (10%) target speed, or 1 second after reaching target speed, whichever is first
                
                time.sleep(sleepInterval) 
            
        except KeyError:
                pass #We would rather just skip if we cannot get good data rather than have our stuff error out
        except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            print("\nExiting.")
            filePath, fileCreated = writeFile(vehicle,rollingGpsData,fileCreated,filePath)
        else:
            if not counter == 0: #dont write to the file on exit if we just wrote to it 
                filePath, fileCreated = writeFile(vehicle,rollingGpsData,fileCreated,filePath)
                print("Saved data:",rollingGpsData)
                print("Finished collecting data")
                #Write the rest of the data when we exit the while loop
            print(gpsData)
            totend = time.time() - totstart
            print("\nCompleted in:",totend)

print("gps class done")

if __name__ == "__main__": # I think we don't technically need this since we won't be importing this file into anything probably

    accThread = accThr()
    gpsThread = gpsThr()
    accThread.start()
    gpsThread.start()

    try: #since both our gps and accelerometer are running in separate threads, we use this to be able to catch keyboard exceptions whenever we want
        while True:
            time.sleep(1)
            print("running")

    except KeyboardInterrupt:
        print("Attempting to close threads...")
        accThread.running = False
        gpsThread.running = False
        accThread.join()
        gpsThread.join()
        print("Threads successfully closed.")