#!/usr/bin/python

import sys
import time
import math
import IMU
import datetime
import os
import numpy


targetHz = 50 #Target frequency to run at 
targetS = 1/targetHz
#Ideally, we want to align our refresh rate with a multiple of our gps refresh rate so we can grab relevant accelerometer data.
#GPS data is precisely aligned to seconds i.e. at 5Hz signals are sent from gps at 03:21:15.00, 03:21:15.20, etc. (I think, this may not include time offset to our location)

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40              # Complementary filter constant
MAG_LPF_FACTOR = 0.4    # Low pass filter constant magnetometer
ACC_LPF_FACTOR = 0.4    # Low pass filter constant for accelerometer

lastTime = time.time()


################# Compass Calibration values ############
# Use calibrateBerryIMU.py to get calibration values
# Calibrating the compass isnt mandatory, however a calibrated
# compass will result in a more accurate heading value.

magXmin =  122893
magYmin =  123672
magZmin =  123152
magXmax =  138807
magYmax =  139808
magZmax =  140640



############### END Calibration offsets #################



gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0
CFangleXFiltered = 0.0
CFangleYFiltered = 0.0
kalmanX = 0.0
kalmanY = 0.0
oldXMagRawValue = 0
oldYMagRawValue = 0
oldZMagRawValue = 0
oldXAccRawValue = 0
oldYAccRawValue = 0
oldZAccRawValue = 0

a = datetime.datetime.now()



 
IMU.detectIMU()     #Detect if BerryIMU is connected.

IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass

# Instantiate algorithms



while True:
    

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


    ##Calculate loop Period(LP). How long between Gyro Reads
    b = datetime.datetime.now() - a
    a = datetime.datetime.now()
    LP = b.microseconds/(1000000*1.0) #loop time
    outputString = "Loop Time %5.5f " % ( LP )
    print(outputString)
    delta_time = LP



    print(outputString)
    #slow program down a bit, makes the output more readable
    delTime = time.time()-lastTime
    if (delTime) < targetS:
        print("\nSurplus time:",targetS-delTime)
        time.sleep(targetS-delTime)

    lastTime = time.time()
    #EFrameAccel
