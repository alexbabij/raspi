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


IMU.detectIMU()     #Detect if BerryIMU is connected.
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass


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
    MAGx  = MAGx * (1.0/16384.0)  #18 bits
    MAGy  = MAGy * (1.0/16384.0)  #18 bits
    MAGz  = MAGz * (1.0/16384.0)  #18 bits

    yG = (ACCx * 0.244)/1000 * fGrav
    xG = (ACCy * 0.244)/1000 * fGrav
    zG = (ACCz * 0.244)/1000 * fGrav
    print("##### X = %fm/s^2  ##### Y =   %fm/s^2  ##### Z =  %fm/s^2  #####" % ( yG, xG, zG))
    print("##### MAGx = %fuT  ##### MAGy =   %fuT  ##### MAGz =  %fuT  #####" % ( MAGx, MAGy, MAGz))



    #slow program down a bit, makes the output more readable
    #time.sleep(0.03)
