#!/usr/bin/python

import sys
import time
import math
import IMU
import datetime
import os
import numpy
import imufusion
import threading as tr





targetHz = 50 #Target frequency to run at 
targetS = 1/targetHz
#Ideally, we want to align our refresh rate with a multiple of our gps refresh rate so we can grab relevant accelerometer data.
#GPS data is precisely aligned to seconds i.e. at 5Hz signals are sent from gps at 03:21:15.00, 03:21:15.20, etc. (I think, this may not include time offset to our location)



#aStart = datetime.datetime.now()
#lastTime = time.time()


 
IMU.detectIMU()     #Detect if BerryIMU is connected.

IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass

# Instantiate algorithms
sample_rate = targetHz #Hz
offset = imufusion.Offset(sample_rate)
ahrs = imufusion.Ahrs()
accLock = tr.Lock()
accDataMag = [0.0,0.0,0.0,0.0,0.0,0.0,0.0] #initialize these two to false so we can compare to them
#Format is: [magnitude of acceleration in earth frame, pi timestamp, pi frame linear acceleration x, y, z]

ahrs.settings = imufusion.Settings(imufusion.CONVENTION_NWU,  # convention
                                   0.5,  # gain
                                   10,  # acceleration rejection
                                   20,  # magnetic rejection
                                   5 * sample_rate)  # rejection timeout = 5 seconds

#The madgwick filter here is actually very fast, but we are limited by the refresh rate we have set for our accelerometer (100Hz), 
#meaning as currently configured, we cannot loop this faster than every 0.01 seconds

#Timestamps of lastest gps and accelerometer data readings
gpsSampTS = [time.time()]
accSampTS = [time.time()]
#currently kinda unused, this would be for synchronizing the gps and accelerometer so you have a better chance of getting up to date data
#as it stands, not really worth it to implement since we are at most off by around 1 cycle + read time = 0.02+0.01 = 0.03 seconds
#which is kind of negligible compared to our gps sampling rate of 0.2 seconds

class accThr(tr.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        #self.aStart = datetime.datetime.now()
        #self.lastTime = time.time()
        with open('configDevice.txt') as mycfgfile:
            config = mycfgfile.read().splitlines() #Read in each line as a list i.e. [a:1, b:2]
            config.pop(0) #Remove the first line from our config file, it is just a description and we don't want it in here
            config = dict([eachLine.split(":") for eachLine in config]) #Split by ":" and turn into dict
            #If this doesn't work, need to move working directory or change to ../configDevice.txt maybe
        self.accMin = float(config["acceleration threshold"])
        self.accInitTime = float(config['accelerometer initialization time'])
        self.accStarted = False
        self.startTime = time.time()
            
    
    def run(self):
        lastTime = time.time()
        aStart = datetime.datetime.now()

        RAD_TO_DEG = 57.29578
        M_PI = 3.14159265358979323846
        G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
        AA =  0.40              # Complementary filter constant
        MAG_LPF_FACTOR = 0.4    # Low pass filter constant magnetometer
        ACC_LPF_FACTOR = 0.4    # Low pass filter constant for accelerometer




        ################# Compass Calibration values ############
        # Use calibrateBerryIMU.py to get calibration values
        # Calibrating the compass isnt mandatory, however a calibrated
        # compass will result in a more accurate heading value.

        #1dot IMU : (deg/s)S
        gyrOffsetX = 1.43
        gyrOffsetY = -2.875
        gyrOffsetZ = -0.55
        accScale = 1.0 
        magXmin =  122225 #These in theory should be recalculated often since they are affected by magnets
        magYmin =  122984
        magZmin =  122504
        magXmax =  138604
        magYmax =  139516
        magZmax =  140280


        ############### END Calibration offsets #################



        gyroXangle = 0.0
        gyroYangle = 0.0
        gyroZangle = 0.0
        oldXMagRawValue = 0
        oldYMagRawValue = 0
        oldZMagRawValue = 0
        oldXAccRawValue = 0
        oldYAccRawValue = 0
        oldZAccRawValue = 0

        #global accDataMag
        print("acc rec started")
        while self.running == True:
            
            lastTime = time.time()
            #Read the accelerometer,gyroscope and magnetometer values
            ACCx = IMU.readACCx()
            ACCy = IMU.readACCy()
            ACCz = IMU.readACCz()
            GYRx = IMU.readGYRx()
            GYRy = IMU.readGYRy()
            GYRz = IMU.readGYRz()
            MAGx = IMU.readMAGx()
            MAGy = IMU.readMAGy()
            MAGz = IMU.readMAGz()
            with accLock:
                accSampTS[0] = time.time()
            
            bFin = datetime.datetime.now() - aStart
            aStart = datetime.datetime.now()
            LP = bFin.microseconds/(1000000*1.0) #loop time
            outputString = "Loop Time %5.5f " % ( LP )
            #print(outputString)
            delta_time = LP

            #Apply compass calibration
            MAGx -= (magXmin + magXmax) /2
            MAGy -= (magYmin + magYmax) /2
            MAGz -= (magZmin + magZmax) /2

            #Times raw mag by sensitivity  
            MAGx  = MAGx * (1.0/16384.0)  #18 bits
            MAGy  = MAGy * (1.0/16384.0)  #18 bits
            MAGz  = MAGz * (1.0/16384.0)  #18 bits


            ##Calculate loop Period(LP). How long between Gyro Reads
            

            ###############################################
            #### Apply low pass filter ####
            ###############################################
            MAGx =  MAGx  * MAG_LPF_FACTOR + oldXMagRawValue*(1 - MAG_LPF_FACTOR);
            MAGy =  MAGy  * MAG_LPF_FACTOR + oldYMagRawValue*(1 - MAG_LPF_FACTOR);
            MAGz =  MAGz  * MAG_LPF_FACTOR + oldZMagRawValue*(1 - MAG_LPF_FACTOR);
            ACCx =  ACCx  * ACC_LPF_FACTOR + oldXAccRawValue*(1 - ACC_LPF_FACTOR);
            ACCy =  ACCy  * ACC_LPF_FACTOR + oldYAccRawValue*(1 - ACC_LPF_FACTOR);
            ACCz =  ACCz  * ACC_LPF_FACTOR + oldZAccRawValue*(1 - ACC_LPF_FACTOR);

            oldXMagRawValue = MAGx
            oldYMagRawValue = MAGy
            oldZMagRawValue = MAGz
            oldXAccRawValue = ACCx
            oldYAccRawValue = ACCy
            oldZAccRawValue = ACCz

            #Convert Gyro raw to degrees per second, also apply our offset
            rate_gyr_x =  GYRx * G_GAIN - gyrOffsetX
            rate_gyr_y =  GYRy * G_GAIN - gyrOffsetY
            rate_gyr_z =  GYRz * G_GAIN - gyrOffsetZ

            #Convert accelerometer data to g's
            ACCx = (ACCx * 0.244)/1000
            ACCy= (ACCy * 0.244)/1000
            ACCz= (ACCz * 0.244)/1000

            #Convert magnetometer to uT from G
            MAGx  = MAGx * 100
            MAGy  = MAGy * 100
            MAGz  = MAGz * 100

            
            gyroscope = numpy.array([rate_gyr_x,rate_gyr_y,rate_gyr_z])
            accelerometer = numpy.array([ACCx, ACCy, ACCz])
            magnetometer = numpy.array([MAGx, MAGy, MAGz])
            euler = numpy.array([0.0,0.0,0.0])
            ACCearthFrame = numpy.array([0.0,0.0,0.0])
            ACCLinear = numpy.array([0.0,0.0,0.0])
            ##################### END Data Collection ########################
            #The documentation is cheeks, this link has some of? the different python functions: https://github.com/xioTechnologies/Fusion/blob/main/Python/Python-C-API/Ahrs.h
            #and https://github.com/xioTechnologies/Fusion/tree/main/Python/Python-C-API should contain all the functions
            #look for PyMethodDef and PyGetSetDef 

            ahrs.update(gyroscope, accelerometer, magnetometer, delta_time)
            euler = ahrs.quaternion.to_euler() #This one is technically a function call
            ACCearthFrame = ahrs.earth_acceleration #These ones are numpy array objects, this one is acceleration in earth frame with gravity removed
            ACCLinear = ahrs.linear_acceleration #acceleration in device frame with gravity removed
            ACCmagnitudeE = math.sqrt(ACCearthFrame[0]*ACCearthFrame[0] + ACCearthFrame[1]*ACCearthFrame[1] + ACCearthFrame[2]*ACCearthFrame[2])
            ACCmagnitudeL = math.sqrt(ACCLinear[0]*ACCLinear[0] + ACCLinear[1]*ACCLinear[1] + ACCLinear[2]*ACCLinear[2])
            
            #accDataMag = ACCmagnitudeE
            sampleTime = time.time()
            with accLock:
                #Python is weird, if I were to do accDataMag = ACCmagnitudeE, this would not update the global variable, because python would create a new 
                #local variable in the scope of this function also named accDataMag. To be able to do it this way, I would need to declare global accDataMag 
                #to make the variable global inside of the scope of the function?
                #The below does work though, and updates the global variable, assumably because it tries to access the index of the global variable instead of 
                #trying to create a new one 
                accDataMag[0] = ACCmagnitudeE
                accDataMag[1] = sampleTime
                accDataMag[2:5] = ACCLinear #using : skips the last index i.e. skips index 5 so pulls: 2,3,4
               


                #accDataMag = ACCmagnitudeE
                
            if (self.accStarted==False) and (ACCmagnitudeE >= self.accMin) and (time.time() >= (self.startTime + self.accInitTime)): #and is shortcircuit, & is not
                #We need to wait for the filter to initialize first, though 
                with accLock:
                    accDataMag[5] = ACCmagnitudeE
                    accDataMag[6] = sampleTime # - 100 #DEBUG
                self.accStarted = True
                #This should only run once and will log the first time that the acceleration threshold is crossed so that #collect_gpsdata can get the actual first
                #instance where the accleration threshold was reached, while still being able to run at a different frequency 
                
            
            if 0: #easy disable all the print statements
                if 0:                       #Change to '0' to stop  showing the angles from the gyro
                    outputString +="\t# GYRX Angle %5.4f  GYRY Angle %5.4f  GYRZ Angle %5.4f # " % (gyroXangle,gyroYangle,gyroZangle)

                if 0:                       #Change to '0' to stop  showing the heading
                    outputString +="\n# EulerX %5.4f  EulerY %5.4f Eulerz %5.4f#" % (euler[0],euler[1],euler[2])

                if 0:                       #Change to '0' to stop showing the acceleration
                    outputString +="\n#Raw ACCx %5.4f  ACCy %5.4f  ACCz %5.4f #" % (ACCx,ACCy,ACCz)
                
                if 1:                       #Change to '0' to stop showing the acceleration
                    outputString +="\n# EarthACCx %5.4f  EarthACCy %5.4f  EarthACCz %5.4f #" % (ACCearthFrame[0],ACCearthFrame[1],ACCearthFrame[2])
                if 0:                       #Change to '0' to stop showing the acceleration
                    outputString +="\n# LinearACCx %5.4f  LinearACCy %5.4f  LinearACCz %5.4f #" % (ACCLinear[0],ACCLinear[1],ACCLinear[2])
                if 0:                       #Change to '0' to stop showing the acceleration
                    outputString +="\n# EarthMagnitude %5.4f  LinearMagnitude  %5.4f #" % (ACCmagnitudeE,ACCmagnitudeL)
                # if 1:                       #Change to '0' to stop showing the acceleration
                #     outputString +="\n# EarthACCx %5.4f  EarthACCy %5.4f  EarthACCz %5.4f #" % (EFrameAccel[0],EFrameAccel[1],EFrameAccel[2])

                print(outputString)

            
            #Make our script refresh at a consistent rate
            delTime = time.time()-lastTime
            if (delTime) < targetS:
                #print("\nSurplus time:",targetS-delTime)
                time.sleep(targetS-delTime)

            
            #EFrameAccel

print("acc class done")


#Note: My gyro on this gps is broken? and super noisy for some reason, same as on the other one I tried 
# (although this one is worse) Im talking +/-25 deg/s on the z-axis between consecutive readings which is insanely bad. 
#My fix for this is to not deal with it. There is also some offset error in the xyz gyro readings. These are compensated for
#by taking the average readings (deg/s) while it is sitting completely still for a few minutes, then using those to correct
#the offset errors. I should eventually get around to finding the source of the noise for this, but for now, it really 
#doesnt matter, since currently, the accelerometer is only really used to determine the start of a 0-60 run, so we have a pretty big
#margin of error to consider a run "started".
#The gyro reading is used in this madgwick filter to calculate the quaternion used to subtract the force of gravity from our accelerometer
#readings. This means that as long as we fix the offset error, and the quaternion isnt super misaligned, we will mostly subtract
#out gravity along the correct vector, giving us a nearish to zero resultant accelerometer reading when at rest.
#If the quaternion is misaligned, its actually pretty bad, since we can end up "adding" additional acceleration. 
#(Think if you add the gravity vector upside down, you now are measuring 2g of acceleration (but to  a lesser extent in our case)).

#Since we are currently working with just the magnitude of the device (car) acceleration to determine our start point, 
#We can technically avoid the filter completely, and do the following:
#Take magnitude of raw xyz acceleration: sqrt(0.1^2 + -0.04^2 + 1^2) = m = 1.00578, sqrt(m^2 -1) = sqrt(a_x^2 + a_y^2) 
#sqrt(a_x^2 + a_y^2) = acceleration with force of gravity removed. 
#This ONLY works if we assume that our only accelerations besides gravity are perpendicular to the force of gravity
#Or in other words, we only have acceleration in the a_x and a_y axes (in the Earth frame), and CANNOT have any acceleration
#other than gravity in the a_z direction. In the device frame, the measured accelerations will be different 
# i.e. a_x = -0.6, a_y = 0.8, a_z = 0.1077, if the device is not perfectly aligned to the Earth frame, but this doesn't matter,
#and the calculation still works, as long as the above assumptions are met.
#This is not actually a completely unreasonable assumption to make, since a proper 0-60 run should be performed on flat
#ground, and we only care about the magnitude of the acceleration, not total acceleration for starting 0-60 runs.
