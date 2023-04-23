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
displayUnits = config["units"]
vehicle = config["current vehicle"]
cutoffSpeed = float(config["max speed"])/conversionDict[config["units"]]
accMin = float(config["acceleration threshold"]) #minimum acceleration to start actually recording the data we read.
#This includes a buffer of data taken before reaching this acceleration value. Intended use is to set minimum 
#acceleration threshold to be considered as having actually started your 0-60 run
screenRefreshRate = float(config["screen refresh rate"])

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




sys.path.append(os.path.join(os.path.dirname(__file__), 'accelerometer'))
#This adds the folder "accelerometer to the path python searches in to import stuff"
#from collect_accel_madgwick import *
from accelerometer.collect_accel_madgwick import *


from fileSave import *
gpsSampTS = [time.time()]

class gpsThr(tr.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.dataOut = []
        self.runStart = 0.0
        
        


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
            collectingData = False
            totstart = time.time()
            gpsData = []
            rollingGpsData = []
            counter = 0
            print("gps rec started")
            currentData = ['',float('nan'),0.0,0.0,0.0]
            #currentData.extend(accDataMag) #could use + instead to concatenate this to the list, doing it with .extend() modifies the same variable in memory
            #while using + creates a new variable with the same name
            prevData = False
            #global accDataMag
            while (self.running == True) & (time.time() < totSamplesC):
                
                report = gpsd.next()
                if report['class'] == 'TPV': 
                #This a lame way to select the correct json object since gpsd will return multiple different objects in repeating order
                    
                    if (math.isfinite(getattr(report,'speed',float('nan')))) & (getattr(report,'time','') !=''):
                    #If the data is bad we just ignore it, the format for this is to return NaN for numbers and empty for strings: ''
                    #Not sure how much an effect on performance this has

                        
                        
                        #We record gps time, velocity, and time offset since starting script as measured by the pi
                        with accLock:
                            curAccDataMag = accDataMag[0]
                            accTime = accDataMag[1]
                            print("accDataMag",accDataMag[0])
                        
                        print("currentData",currentData)
                      
                        print("counter",counter)
                       
                        #Our format is: [gps time(yyyy-mm-ddThr:min:ms), gps speed(m/s), pi time offset(s), accelerometer acceleration in earth frame(G), 
                                                            # difference between time of this measurement and accel measurement(s)]
                        currentData = [getattr(report,'time',''),getattr(report,'speed','nan'),(time.time()-totstart),curAccDataMag,(time.time()-accTime)]
                        #currentData[:3] = [getattr(report,'time',''),getattr(report,'speed','nan'),(time.time()-totstart)]
                        #doing it this way somehow manages to also update the value in gpsData after this step, I think this may have to do with the
                        #same weirdness that lets me update accDataMag without declaring it a global variable, because gpsData is assigned the same object
                        #in memorry as currentData, meaning if I simply update currentData's elements, it also updates gpsData, whereas if I redeclare
                        #currentData = [...], I think it makes a new thing. we can get around this by using .copy() instead of just gpsData = currentData

                        #We should never get nan or an empty string since we check for it, but just in case, we don't want this to stop collecting data
                        #We are capable of getting duplicate results, so we filter them out
                        
                        #we want to have the acceleration value variable locked for as little time as possible
                        
                        if curAccDataMag >= accMin:
                            collectingData = True
                            self.runStart = time.time()

                        if prevData == False:
                            rollingGpsData.append(currentData)
                            prevData = currentData
                            self.dataOut = currentData
                            
                            print("Time since start:",time.time()-totstart)
                            print(currentData)
                            with accLock:
                                gpsSampTS[0] = time.time() #timestamp of when latest gps sample became available

                        elif (prevData[0] != currentData[0]):
                            prevData = currentData
                            rollingGpsData.append(currentData)
                            if (not collectingData) & (len(rollingGpsData) > samplesC):
                                #rollingGpsData normally gets saved every 1 second (actually comes from "storage inteval" setting) so its length should correspond to that 
                                #i.e. if at sampling at 5Hz and saving every 1 second, this should always be of length 5. It is nice to have some data before we
                                #reach our "starting" acceleration though, so we keep a rolling list of the last 1 seconds of measurements until collectingData = True
                                rollingGpsData = rollingGpsData[len(rollingGpsData)-samplesC:] 
                                #this covers the case where its randomly longer than 11 which it should never be
                                #This in effect inserts the 1 second of data before we reach our target acceleration into our log txt file
                                print("len(rollingGpsData)",len(rollingGpsData))
                            if collectingData: 
                                gpsData.append(currentData)
                                counter += 1

                        if collectingData & (len(gpsData)==0):
                            gpsData.append(currentData)
                            counter += 1 #We save our file after 1 second of data collection while collectingData = true

                            print("Time since start:",time.time()-totstart)
                            print(currentData)
                        
                            
                    # end = time.time()
                    # elapsed = (end-start)
                    # start = time.time()
                    #print('\nTime/refresh',elapsed)
                    if collectingData:
                        if (counter >= samplesC):
                            filePath, fileCreated = writeFile(vehicle,rollingGpsData,fileCreated,filePath)
                            counter = 0
                            print("Saved data:",rollingGpsData)
                            rollingGpsData = []
                            
                        if gpsData[-1][1] >= (cutoffSpeed*1.1):
                            collectingData = False
                            #self.running = False
                        
                        if gpsData[-1][1] >= (cutoffSpeed):
                            collectingData = False
                            #self.running = False
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

from display_text import *
#This is our display class, we can call the function dispText to write text to the screen with a few input parameters
#Our display connection was setup when we imported the display_text file. Probably not the bet way to do this.
class piScreen(tr.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.refreshRate = 1/screenRefreshRate #I dont think this is even necessary

        
    
    def run(self):
        totrefreshTime = 0.0

        startTime = time.time()
        data = gpsThread.dataOut.copy()
        velocity = data[1] * conversionDict[displayUnits]#convert from m/s to selected units
        elapsedTime = time.time()-gpsThread.runStart #s
        #construct our string to write to the screen
        #This is the quick and dirty way. If we instead implement a function to just draw individual text blocks at given xy locations, we can vary
        #things like font size, color, etc. on a per character basis if we really wanted to, since we can draw successive things into an image,
        #then we write that image to the screen
        string = "Elapsed Time:",str(round(elapsedTime,2))+"s","\nVelocity:",str(round(velocity,1)),displayUnits
        string += "\nRefresh:",str(round(1/totrefreshTime,1))+"fps"
        dispText(string,"nw",[255,255,255,255],15)
        elapsedR = time.time()-startTime
        #attempt to refresh at the selected rate, if not possible, refresh as fast as possible
        if (self.refreshRate) > elapsedR:
            time.sleep(self.refreshRate-elapsedR)
        totrefreshTime = time.time()-startTime


if __name__ == "__main__": # I think we don't technically need this since we won't be importing this file into anything probably. 
                            #stuff in here wont run if we import this into something
    dispBackground([0,0,0]) #Set display screen to black background
    dispText("Starting","center",[255,255,255,255],25)
    accThread = accThr()
    gpsThread = gpsThr()
    accThread.start()
    time.sleep(1) #have the accelerometer script start first so the values in it can start to even out since it is running a madgwick filter
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