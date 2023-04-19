#!/usr/bin/python
#
#       This program demonstrates how to convert the raw values from an accelerometer to Gs
#
#
#       Feel free to do whatever you like with this code.
#       Distributed as-is; no warranty is given.
#
#       https://ozzmaker.com/accelerometer-to-g/


import time
import IMU
import sys
import datetime
import math
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

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40              # Complementary filter constant
MAG_LPF_FACTOR = 0.4    # Low pass filter constant magnetometer
ACC_LPF_FACTOR = 0.4    # Low pass filter constant for accelerometer
ACC_MEDIANTABLESIZE = 9         # Median filter table size for accelerometer. Higher = smoother but a longer delay
MAG_MEDIANTABLESIZE = 9         # Median filter table size for magnetometer. Higher = smoother but a longer delay

IMU.detectIMU()     #Detect if BerryIMU is connected.
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass
#calibration data
magXmin =  122893
magYmin =  123672
magZmin =  123152
magXmax =  138807
magYmax =  139808
magZmax =  140640

fGrav = 9.80674 #m/s^2 Force of gravity in Spokane, WA
a = datetime.datetime.now()

while True:
 
 ##Calculate loop Period(LP). How long between Gyro Reads
    b = datetime.datetime.now() - a
    a = datetime.datetime.now()
    LP = b.microseconds/(1000000*1.0)
    outputString = "Loop Time %5.5f " % ( LP )
    print(outputString)

    #Read the accelerometer,gyroscope and magnetometer values, once being turned into values, is measured in G's, convert to m/s: 
    ACCx = IMU.readACCx()
    ACCy = IMU.readACCy()
    ACCz = IMU.readACCz()
    MAGx = IMU.readMAGx() 
    MAGy = IMU.readMAGy() 
    MAGz = IMU.readMAGz() 
    #Apply compass calibration
    MAGx -= (magXmin + magXmax) /2
    MAGy -= (magYmin + magYmax) /2
    MAGz -= (magZmin + magZmax) /2

    MAGx =  MAGx  * MAG_LPF_FACTOR + oldXMagRawValue*(1 - MAG_LPF_FACTOR);
    MAGy =  MAGy  * MAG_LPF_FACTOR + oldYMagRawValue*(1 - MAG_LPF_FACTOR);
    MAGz =  MAGz  * MAG_LPF_FACTOR + oldZMagRawValue*(1 - MAG_LPF_FACTOR);
    ACCx =  ACCx  * ACC_LPF_FACTOR + oldXAccRawValue*(1 - ACC_LPF_FACTOR);
    ACCy =  ACCy  * ACC_LPF_FACTOR + oldYAccRawValue*(1 - ACC_LPF_FACTOR);
    ACCz =  ACCz  * ACC_LPF_FACTOR + oldZAccRawValue*(1 - ACC_LPF_FACTOR);

    MAGx  = MAGx * (1.0/16384.0) *100 #18 bits
    MAGy  = MAGy * (1.0/16384.0) *100 #18 bits
    MAGz  = MAGz * (1.0/16384.0) *100 #18 bits
    rsm = math.sqrt(MAGx*MAGx + MAGy*MAGy + MAGz*MAGz)

    yG = (ACCx * 0.244)/1000 * fGrav
    xG = (ACCy * 0.244)/1000 * fGrav
    zG = (ACCz * 0.244)/1000 * fGrav
    print("##### X = %fm/s^2  ##### Y =   %fm/s^2  ##### Z =  %fm/s^2  #####" % ( yG, xG, zG))
    print("##### MAGx = %fuT  ##### MAGy =   %fuT  ##### MAGz =  %fuT  ##### rsm = %fuT" % ( MAGx, MAGy, MAGz, rsm))



    #slow program down a bit, makes the output more readable
    #time.sleep(0.03)
