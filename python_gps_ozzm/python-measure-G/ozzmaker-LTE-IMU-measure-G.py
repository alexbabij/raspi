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



IMU.detectIMU()     #Detect if BerryIMU is connected.
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass


fGrav = 9.80674 #m/s^2 Force of gravity in Spokane, WA

while True:


    #Read the accelerometer,gyroscope and magnetometer values, once being turned into values, is measured in G's, convert to m/s: 
    ACCx = IMU.readACCx()
    ACCy = IMU.readACCy()
    ACCz = IMU.readACCz() 
    yG = (ACCx * 0.244)/1000 * fGrav
    xG = (ACCy * 0.244)/1000 * fGrav
    zG = (ACCz * 0.244)/1000 * fGrav
    print("##### X = %fm/s^2  ##### Y =   %fm/s^2  ##### Z =  %fm/s^2  #####" % ( yG, xG, zG))



    #slow program down a bit, makes the output more readable
    time.sleep(0.03)
