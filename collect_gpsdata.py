#! /usr/bin/python
#Running this file will collect gps data at the specified interval 
from gps import *
import os
import sys
import time
import math
import subprocess
import threading as tr #we don technically need this since threading gets imported in madgwick_filters
from gpiozero import Button





#Configure gps settings including update rate
with open('configDevice.txt') as mycfgfile:
    config = mycfgfile.read().splitlines() #Read in each line as a list i.e. [a:1, b:2]
    config.pop(0) #Remove the first line from our config file, it is just a description and we don't want it in here
    config = dict([eachLine.split(":") for eachLine in config]) #Split by ":" and turn into dict
updateRate = int(config["updateRate"])
sleepInterval = 1/(updateRate*10) #Maybe tweak this depending on performance
#gpsd is weird, and while it should be waiting to return a NEW report every time we query it, it doesn't and will return around 4 TPV
#reports, regardless of how long we wait to query it again in our loop, idk. The above works and doesn't cause it to lag or take longer
#than the interval it is timing to run the entire function, unlike using something like:1/(updateRate*2)

#The speed reading that comes out of gpsd is in m/s, this dictionary stores the conversion factor from m/s to [key]
accInitTime = float(config['accelerometer initialization time'])
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


global gpsData

sys.path.append(os.path.join(os.path.dirname(__file__), 'accelerometer'))
#This adds the folder "accelerometer to the path python searches in to import stuff"
#from collect_accel_madgwick import *
from accelerometer.collect_accel_madgwick import *

class exitGps(Exception): #currently unused
    pass

def whenPressed():
    print('\n\nbutton pressed\n\n') #DEBUG
    gpsThread.restart()
    ##buttonEnabled = False 
    #gpsThread.

buttongps = Button(21)    
buttongps.when_pressed = whenPressed

from fileSave import *


class gpsThr(tr.Thread):
    def __init__(self):
        super().__init__()
        # self.running = True
        # self.dataOut = [0.0]*5 #initialize with values so other things can still use it as normal
        # self.runStart = False
        # self.accMag = 0.0
        # self.runComplete = False
        # self.timedOut = False
        # self.restart()
        gpsSampTS = [time.time()]

        
    def restart(self):
        self.running = True
        self.dataOut = [0.0]*5 #initialize with values so other things can still use it as normal
        self.runStart = False
        self.accMag = 0.0
        self.runComplete = False
        self.timedOut = False
        gpsSampTS = [time.time()]

        #write our data to a file every 1 second 
        self.samplesC = int(config["storage interval"]) * updateRate #Only whole second intervals are allowed otherwise this counter could be a decimal
            
        #Basically a timeout in case we don't stop taking data within timeout period, this starts when we hit our minimum acceleration
        self.globalTimeout = float(config["global timeout"]) + time.time() #This one starts when we run this, not when we hit minimum acceleration
        self.filePath = ""
        self.fileCreated = False
        self.collectingData = False
        self.totstart = time.time()
        
        
        self.rollingGpsData = []
        self.counter = 0
        self.finSampCounter = 0
        self.totSamplesC = 0.0
        
        self.currentData = ['',float('nan'),0.0,0.0,0.0]
        #self.currentData.extend(accDataMag) #could use + instead to concatenate this to the list, doing it with .extend() modifies the same variable in memory
        #while using + creates a new variable with the same name
        self.prevData = False
        self.usedSats = -1

        #We need to clear previous instance of single acceleration value:
        with accLock:
            accDataMag[5] = 0.0
            accDataMag[6] = 0.0 # - 100 #DEBUG
            accThread.accStarted = False

        print('gps data restarted')
        print("gps rec started")

    def run(self):
        #this function definition of run(self) is a special method from threading. this function will automatically run when .start() is used 

        try:
            self.restart()
            global gpsData
            gpsData = []
            start = time.time() #DEBUG
            gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)
            
            debug1 = True #DEBUG

            #global accDataMag
            while (self.running == True):
                #print('gps running') #DEBUG
                report = gpsd.next()

                if report['class'] == 'SKY':
                    self.usedSats = getattr(report,'uSat',-1)
                    #print('self.usedSats',self.usedSats) #DEBUG

                if report['class'] == 'TPV': 
                #This a lame way to select the correct json object since gpsd will return multiple different objects in repeating order
                    
                    if (math.isfinite(getattr(report,'speed',float('nan')))) & (getattr(report,'time','') !=''):
                    #If the data is bad we just ignore it, the format for this is to return NaN for numbers and empty for strings: ''
                    #Not sure how much an effect on performance this has
                        
                        # print('GPS frequency:',str(time.time()-start)) #DEBUG
                        # start = time.time() #DEBUG
                        
                        with accLock:
                            #extract data from the accelerometer
                            accData = accDataMag.copy()
                            #print("accDataMag",accDataMag[0]) #DEBUG
                        curAccDataMag = accData[0]
                        accTime = accData[1]
                        
                            
                        
                        #print("self.currentData",self.currentData) #DEBUG
                      
                        #print("self.counter",self.counter) #DEBUG
                       
                        if (accData[5] >= accMin) and (self.runComplete == False):
                            self.collectingData = True #This could be inside the if statement below
                            
                            if (self.runStart == False):
                                self.runStart = time.time()
                                self.totSamplesC = float(config["timeout"]) + time.time()
                                curAccDataMag = accData[5]
                                accTime = accData[6]
                                print("Accleration Threshold Reached, accData[5]",accData[5])
                                if self.totSamplesC > self.globalTimeout:
                                    self.globalTimeout = self.totSamplesC + 1
                                    #if we would globally timeout before our local timeout, dont
                            #This should run only once, when we first hit our target acceleration
                        #The problem with this is that we are basically hoping to "catch" our acceleration value in a stream that updates 50 times/second
                        #while we are only checking it 5 times/second. We fix this by just reassigning it with our special tracked acceleration and time 
                        #value which is stored in collect_accel_madgwick.py
                        
                        self.accMag = curAccDataMag #We do this so we can use this value outside of gpsThr class (in the screen class piScreen)
                       
                        #Our format is: [gps time(yyyy-mm-ddThr:min:ms), gps speed(m/s), pi time offset(s), accelerometer acceleration magnitude in earth frame(G), 
                                                            # difference between time of this measurement and accel measurement(s)] (5 elements long)
                                                            #our last value here is a negative number, since our data was taken before it was logged. 
                        self.currentData = [getattr(report,'time',''),getattr(report,'speed','nan'),(time.time()-self.totstart),curAccDataMag,(accTime-time.time())]
                        #self.currentData[:3] = [getattr(report,'time',''),getattr(report,'speed','nan'),(time.time()-self.totstart)]
                        #doing it this way somehow manages to also update the value in gpsData after this step, I think this may have to do with the
                        #same weirdness that lets me update accDataMag without declaring it a global variable, because gpsData is assigned the same object
                        #in memorry as self.currentData, meaning if I simply update self.currentData's elements, it also updates gpsData, whereas if I redeclare
                        #self.currentData = [...], I think it makes a new thing. we can get around this by using .copy() instead of just gpsData = self.currentData

                        #We should never get nan or an empty string since we check for it, but just in case, we don't want this to stop collecting data
                        #We are capable of getting duplicate results, so we filter them out
                        
                        #we want to have the acceleration value variable locked for as little time as possible


                        # #DEBUG
                        # #print('self.collectingData',self.collectingData) #DEBUG
                        # if debug1 & (self.collectingData & (time.time() > self.runStart+5)):
                        #     #Run this after 10 seconds of data collection
                        #     self.currentData = ['debug',(cutoffSpeed+1),(time.time()-self.totstart),curAccDataMag,(accTime-time.time())]
                        #     debug1 = False
                        #     print("\n\nran once\n\n") 
                        # #DEBUG 


                        

                        if self.prevData == False: #store previous data if we don't have any yet
                            self.rollingGpsData.append(self.currentData)
                            self.prevData = self.currentData
                            self.dataOut = self.currentData
                            #print("\n\nself.dataOut",self.dataOut,"\n") #DEBUG

                            #print("Time since start:",time.time()-self.totstart)
                            #print(self.currentData) #debug
                            with accLock:
                                gpsSampTS[0] = time.time() #timestamp of when latest gps sample became available

                        elif (self.prevData[0] != self.currentData[0]):#position 0 is the timestamp which will always be present and unique 
                            #print("self.currentData", self.currentData) #DEBUG
                            self.prevData = self.currentData
                            self.dataOut = self.currentData
                            #print("\n\nself.dataOut",self.dataOut,"\n") #DEBUG
                            self.rollingGpsData.append(self.currentData)
                            if (not self.collectingData) & (len(self.rollingGpsData) > self.samplesC):
                                #self.rollingGpsData normally gets saved every 1 second (actually comes from "storage inteval" setting) so its length should correspond to that 
                                #i.e. if at sampling at 5Hz and saving every 1 second, this should always be of length 5. It is nice to have some data before we
                                #reach our "starting" acceleration though, so we keep a rolling list of the last 1 seconds of measurements until self.collectingData = True
                                self.rollingGpsData = self.rollingGpsData[len(self.rollingGpsData)-self.samplesC:] 
                                #this covers the case where its randomly longer than 11 which it should never be
                                #This in effect inserts the 1 second of data before we reach our target acceleration into our log txt file
                                #print("len(self.rollingGpsData)",len(self.rollingGpsData)) #debug
                            if self.collectingData: 
                                if self.runComplete==False:
                                    gpsData.append(self.currentData)

                                #add to counter to save to file after 1 second worth of data 
                                self.counter += 1
                        """
                        if self.collectingData & (len(gpsData)==0):
                            #We cant compare to previous reading if we dont have a previous reading yet, so we log only the first reading with no check
                            gpsData.append(self.currentData)
                            self.counter += 1 #We save our file after 1 second of data collection while self.collectingData = true, self.counter is used to track this

                            print("Time since start:",time.time()-self.totstart)
                            #print(self.currentData) #debug
                            #I think this entire thing is no longer needed
                        """
                            
                    # end = time.time()
                    # elapsed = (end-start)
                    # start = time.time()
                    #print('\nTime/refresh',elapsed)
                    if self.collectingData:
                        if (self.counter >= self.samplesC):
                            self.filePath, self.fileCreated = writeFile(vehicle,self.rollingGpsData,self.fileCreated,self.filePath)
                            #I wrote this before I knew about classes. This is basically the exact use case of a class where we are setting a file
                            #path once and then reusing it in the same function an indeterminate amount of times.
                            self.counter = 0
                            print("Saved data:",self.rollingGpsData)
                            self.rollingGpsData = []
                            
                        if self.finSampCounter >=5 :
                            
                            self.filePath, self.fileCreated = writeFile(vehicle,self.rollingGpsData,self.fileCreated,self.filePath) #Write last data chunk
                            self.collectingData = False
                            self.runComplete = True #should be redundant I think #investigate
                            #This is to allow us to write 5 more samples to the file but not have them in gpsData
                            #self.running = False

                        if gpsData[-1][1] >= (cutoffSpeed):
                            self.totSamplesC = time.time()+100 #Basically disable the timeouts if we get to here so we don't get a weird edge case where we finish 
                            self.globalTimeout = time.time()+100 #our run less than 5 measurements before either of our timeout periods
                            #self.collectingData = False
                            self.runComplete = True
                            #self.running = False
                            
                        if self.runComplete: #and self.collectingData:#investigate if necessary, shouldnt be
                            self.finSampCounter +=1
                            #print("\nFinsample self.counter:\n", self.finSampCounter) #DEBUG
                        if (time.time() > self.totSamplesC) or (time.time() > self.globalTimeout):
                            self.collectingData = False
                            self.runComplete = True
                            self.timedOut = True

                        #Record data up until reaching slightly past (10%) target speed, or 1 second after reaching target speed, whichever is first
                #print("\n\ncollecting data:",self.collectingData) #DEBUG
                time.sleep(sleepInterval) 
            
        except KeyError:
                pass #We would rather just skip if we cannot get good data rather than have our stuff error out
        except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
            print("\nExiting.")
            if self.collectingData:
                self.filePath, self.fileCreated = writeFile(vehicle,self.rollingGpsData,self.fileCreated,self.filePath)
        except exitGps:
            print('Restarting')
            if self.collectingData:
                self.filePath, self.fileCreated = writeFile(vehicle,self.rollingGpsData,self.fileCreated,self.filePath)
            
        else:
            if self.collectingData:
                if not self.counter == 0: #dont write to the file on exit if we just wrote to it 
                    self.filePath, self.fileCreated = writeFile(vehicle,self.rollingGpsData,self.fileCreated,self.filePath)
                    print("Saved data:",self.rollingGpsData)
                    print("Finished collecting data")
                    #Write the rest of the data when we exit the while loop
                print(gpsData)
                totend = time.time() - self.totstart
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

    global gpsData #We dont need to define it as global in here if we dont want to change it 
    
    def run(self):
        totrefreshTime = 1.0 #have to be careful not to initialize to zero since we divide by it
        data = [0.0]*5 # initialize this in case gpsThread.dataout isnt ready yet
        elapsedTime = 0.000
        while self.running:
            startTime = time.time()
            data = gpsThread.dataOut.copy()
            velocity = data[1] * conversionDict[displayUnits]#convert from m/s to selected units
            acceleration = gpsThread.accMag #g's
            if (gpsThread.runComplete == False) and (gpsThread.runStart != False):
                elapsedTime = time.time()-gpsThread.runStart #s
            else:
                elapsedTime = 0.000
            #construct our string to write to the screen
            #This is the quick and dirty way. If we instead implement a function to just draw individual text blocks at given xy locations, we can vary
            #things like font size, color, etc. on a per character basis if we really wanted to, since we can draw successive things into an image,
            #then we write that image to the screen
            refresh = str(round(1/totrefreshTime,1))
            if gpsThread.timedOut:
                string = "Time: Run timed out"
                backgroundColor = [217,7,7] #Red
                fontColor = [255,255,255,255]
                
            elif (gpsThread.timedOut == False) & (gpsThread.runComplete):
                #print("\n\n\nrun complete\n\n\n") #DEBUG
                #print("gpsdata",gpsData) #DEBUG
                #print("Final Time",str(round(self.finalTime(gpsData,cutoffSpeed),2))) #DEBUG
                string = "Completed in: "+str(round(self.finalTime(gpsData,cutoffSpeed),2))+"s"
                backgroundColor = [50,168,82] #Green
                fontColor = [255,255,255,255]
            else:
                string = "Time: "+str(round(elapsedTime,2))+"s"
                backgroundColor = [0,0,0] #Black
                fontColor = [255,255,255,255]




            string+="\nVelocity: "+str(round(velocity,1))+" "+displayUnits
            string += "\nAcceleration: "+str(round(acceleration,2))+"g" #dont forget you can't use commas to combine strings like you could in print()
            string += "\nTarget: "+str(round(cutoffSpeed*conversionDict[displayUnits],0))+"mph"
            
            satsString = str(int(gpsThread.usedSats))+" sats"
            satsfontColor = [255,255,255,255] #White
            satsImg = dispText(satsString,textLoc='sw',fontColor=satsfontColor,backColor=backgroundColor,FONTSIZE=11,refreshRate=False,updateScreen=False)

            dispText(string,"nw",FONTSIZE=14,fontColor=fontColor,backColor=False,refreshRate=refresh,imgIn=satsImg)
            elapsedR = time.time()-startTime
            #attempt to refresh at the selected rate, if not possible, refresh as fast as possible
            if (self.refreshRate) > elapsedR:
                time.sleep(self.refreshRate-elapsedR)
            totrefreshTime = time.time()-startTime

    #Calculates final time from data using accelerometer offsets and linear interpolation of last 2 gps readings
    def finalTime(self,gpsData,cutoffSpeed):
        
        #Our format is: [gps time(yyyy-mm-ddThr:min:ms), gps speed(m/s), pi time offset(s), accelerometer acceleration magnitude in earth frame(G), 
                                                                # difference between time of this measurement and accel measurement(s)] (5 elements long)
                                                                #our last value here is a negative number, since our data was taken before it was logged.

        finVel_2 = gpsData[-1][1] #This should be the first velocity past the threshold since data recording should stop after this point
        finVel_1 = gpsData[-2][1] #This should always be below the next measurement or it would have completed already
        finTime_2 = gpsData[-1][2]
        finTime_1 = gpsData[-2][2]
        if abs(finVel_2-finVel_1) < 1E-5: #dont use == for floats :)
            #We dont want to divide by 0:
            finTime = finTime_2
        else:
            finTime = finTime_1 + (cutoffSpeed-finVel_1) * (finTime_2-finTime_1)/(finVel_2-finVel_1)#linear interpolation

        startVel = gpsData[0][1] #we just kinda assume they started at 0 mph instead of actually using this
        #We could average the rolling data we keep before this starting velocity to try to mitigate the gps noise, but for the purposes of getting 0-60, its not really worth it, since a car doing a 0-60
        #run doesn't have a nice linear acceleration curve, and this curve is different between naturally aspirated, supercharged, turbocharged cars, etc. 
        #The alternative to doing this would be to fit a curve to the entire 0-60 run and then interpolate on that. 
        startTime = gpsData[0][2] -gpsData[0][4]#pi time offset starts from when we turn enable data collection not start the run
        #That means this doesnt start at 0, we also add in the time offset from the accelerometer which should be at best 0 or 
        #usually negative, meaning it pushes back our starttime
            
        runTime = finTime - startTime
        return runTime



dispBackground([0,0,0]) #Set display screen to black background

accThread = accThr()
gpsThread = gpsThr()
dispThread = piScreen()
accThread.start()
accInitTimeWhole, accInitTimeRem = divmod(accInitTime,1)

#have the accelerometer script start first so the values in it can start to even out since it is running a madgwick filter
for i in range(int(accInitTimeWhole),0,-1):
    dispText("Initializing IMU, \ndon't move \nsensor ("+str(round(i+accInitTimeRem,1))+")","center",fontColor=[255,255,255,255],FONTSIZE=15)
    time.sleep(1)
    
dispText("Initializing IMU, \ndon't move \nsensor ("+str(round(0.01+accInitTimeRem,1))+")","center",fontColor=[255,255,255,255],FONTSIZE=15)
time.sleep(accInitTimeRem+0.01)

gpsThread.start()
dispThread.start()



try: #since both our gps and accelerometer are running in separate threads, we use this to be able to catch keyboard exceptions whenever we want
    while True:
        time.sleep(1)
        print("running")

except KeyboardInterrupt:
    print("Attempting to close threads...")
    accThread.running = False
    gpsThread.running = False
    dispThread.running = False
    accThread.join()
    gpsThread.join()
    dispThread.join()
    print("Threads successfully closed.")





    


# """
# Todo:
# display 0-60 time
# integrate with setup_data_collection
# align refresh times of threads
# set gps dynamic mode to vehicle instead of default
# add  pushbutton to stop data collection
# """