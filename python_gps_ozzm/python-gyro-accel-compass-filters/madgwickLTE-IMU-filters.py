#!/usr/bin/python

import sys
import time
import math
import IMU
import datetime
import os
import numpy
import imufusion

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40              # Complementary filter constant
MAG_LPF_FACTOR = 0.4    # Low pass filter constant magnetometer
ACC_LPF_FACTOR = 0.4    # Low pass filter constant for accelerometer
ACC_MEDIANTABLESIZE = 9         # Median filter table size for accelerometer. Higher = smoother but a longer delay
MAG_MEDIANTABLESIZE = 9         # Median filter table size for magnetometer. Higher = smoother but a longer delay



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


'''
Here is an example:
magXmin =  -1748
magYmin =  -1025
magZmin =  -1876
magXmax =  959
magYmax =  1651
magZmax =  708
Dont use the above values, these are just an example.
'''
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
sample_rate = 20 #Hz
offset = imufusion.Offset(sample_rate)
ahrs = imufusion.Ahrs()

ahrs.settings = imufusion.Settings(imufusion.CONVENTION_NWU,  # convention
                                   0.5,  # gain
                                   10,  # acceleration rejection
                                   20,  # magnetic rejection
                                   5 * sample_rate)  # rejection timeout = 5 seconds


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


    #Apply compass calibration
    MAGx -= (magXmin + magXmax) /2
    MAGy -= (magYmin + magYmax) /2
    MAGz -= (magZmin + magZmax) /2

    #Times raw mag by sensitivity  
    MAGx  = MAGx * (1.0/16384.0)  #18 bits
    MAGy  = MAGy * (1.0/16384.0)  #18 bits
    MAGz  = MAGz * (1.0/16384.0)  #18 bits


    ##Calculate loop Period(LP). How long between Gyro Reads
    b = datetime.datetime.now() - a
    a = datetime.datetime.now()
    LP = b.microseconds/(1000000*1.0) #loop time
    outputString = "Loop Time %5.5f " % ( LP )
    print(outputString)
    delta_time = LP

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

    #Convert Gyro raw to degrees per second
    rate_gyr_x =  GYRx * G_GAIN
    rate_gyr_y =  GYRy * G_GAIN
    rate_gyr_z =  GYRz * G_GAIN

    #Convert accelerometer data to g's
    ACCx = (ACCx * 0.244)/1000
    ACCy= (ACCy * 0.244)/1000
    ACCz= (ACCz * 0.244)/1000

    
    gyroscope = [rate_gyr_x,rate_gyr_y,rate_gyr_z]
    accelerometer = [ACCx, ACCy, ACCz]
    magnetometer =
    ##################### END Data Collection ########################

    ahrs.update(gyroscope, accelerometer, magnetometer, delta_time)

    
    if 0:                       #Change to '0' to stop showing the angles from the accelerometer
        outputString += "#  ACCX Angle %5.2f ACCY Angle %5.2f  #  " % (AccXangle, AccYangle)

    if 0:                       #Change to '0' to stop  showing the angles from the gyro
        outputString +="\t# GYRX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f # " % (gyroXangle,gyroYangle,gyroZangle)

    if 1:                       #Change to '0' to stop  showing the angles from the complementary filter
        outputString +="\n#  CFangleX Angle %5.2f   CFangleY Angle %5.2f  #" % (CFangleX,CFangleY)

    if 1:                       #Change to '0' to stop  showing the angles from the Kalman filter
        outputString +="\n# kalmanX %5.2f   kalmanY %5.2f #" % (kalmanX,kalmanY)

    if 0:                       #Change to '0' to stop  showing the angles from the Kalman filter
        outputString +="\n# pitch %5.2f   roll %5.2f #\n" % (pitch*180/M_PI,roll*180/M_PI)

    if 1:                       #Change to '0' to stop  showing the heading
        outputString +="\n# HEADING %5.2f  tiltCompensatedHeading %5.2f #" % (heading,tiltCompensatedHeading)

    if 1:                       #Change to '0' to stop showing the acceleration
        outputString +="\n# ACCx %5.2f  ACCy %5.2f  ACCz %5.2f #" % (ACCxt,ACCyt,ACCzt)
    


    

    if 0:                       #Change to '0' to stop showing the acceleration
        outputString +="\n# dims %5.2f  ACCy %5.2f #" % (rotMatrix.ndim,np.size(rotMatrix))
    if 1:                       #Change to '0' to stop showing the acceleration
        outputString +="\n# EarthACCx %5.2f  EarthACCy %5.2f  EarthACCz %5.2f #" % (EFrameAccel[0],EFrameAccel[1],EFrameAccel[2])

    print(outputString)
    #slow program down a bit, makes the output more readable
    time.sleep(0.03)
    #EFrameAccel
