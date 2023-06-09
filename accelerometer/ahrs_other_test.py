#!/usr/bin/python

import sys
import time
import math
import IMU
import datetime
import os
import numpy
from ahrs.filters import Madgwick
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
madgwick = Madgwick(frequency=50)



#Format is: [magnitude of acceleration in earth frame, pi timestamp, pi frame linear acceleration x, y, z]


#The madgwick filter here is actually very fast, but we are limited by the refresh rate we have set for our accelerometer (100Hz), 
#meaning as currently configured, we cannot loop this faster than every 0.01 seconds

#Timestamps of lastest gps and accelerometer data readings
gpsSampTS = [time.time()]
accSampTS = [time.time()]
#currently kinda unused, this would be for synchronizing the gps and accelerometer so you have a better chance of getting up to date data
#as it stands, not really worth it to implement since we are at most off by around 1 cycle + read time = 0.02+0.01 = 0.03 seconds
#which is kind of negligible compared to our gps sampling rate of 0.2 seconds



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

# magXmin =  122893
# magYmin =  123672
# magZmin =  123152
# magXmax =  138807
# magYmax =  139808
# magZmax =  140640

magXmin =  122318
magYmin =  123508
magZmin =  122284
magXmax =  138371
magYmax =  139716
magZmax =  139848


############### END Calibration offsets #################
#1G = 9.80665 as a standard
#F_grav at calibration location in spokane: 9.80674
#localG = 9.80674/9.80665 = 1.00000917745 = basically negligible
#for 2dot IMU (1st one) avg felt acceleration magnitude while stationary: 1.03226 -> this should = 1G or technically 1.00000917745G
#for 1dot IMU (2nd one) avg felt acceleration magnitude while stationary: 
#Lets scale our acceleration readings by this factor
accScale = 1/1.03226

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
oldXMagRawValue = 0
oldYMagRawValue = 0
oldZMagRawValue = 0
oldXAccRawValue = 0
oldYAccRawValue = 0
oldZAccRawValue = 0

avgMag = 0.0
counter = 0
counter1 = 0

qPrev = numpy.array([0.7071, 0.0, 0.7071, 0.0])
#global accDataMag
print("acc rec started")
while True:
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

    #Convert Gyro raw to degrees per second
    rate_gyr_x =  GYRx * G_GAIN
    rate_gyr_y =  GYRy * G_GAIN
    rate_gyr_z =  GYRz * G_GAIN

    #Convert accelerometer data to g's
    ACCx = (ACCx * 0.244)/1000
    ACCy= (ACCy * 0.244)/1000
    ACCz= (ACCz * 0.244)/1000
    ACCx = ACCx*accScale
    ACCy= ACCy*accScale
    ACCz= ACCz*accScale


    #Convert magnetometer to nT from G
    MAGx  = MAGx * 1E5
    MAGy  = MAGy * 1E5
    MAGz  = MAGz * 1E5

    
    gyroscope = numpy.array([rate_gyr_x,rate_gyr_y,rate_gyr_z])
    accelerometer = numpy.array([ACCx, ACCy, ACCz])
    ACCVec = numpy.array([[ACCx], [ACCy], [ACCz]])
    magnetometer = numpy.array([MAGx, MAGy, MAGz])
    euler = numpy.array([0.0,0.0,0.0])
    rotationMat = numpy.array([[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]])
    ACCearthFrame = numpy.array([0.0,0.0,0.0])
    ACCLinear = numpy.array([0.0,0.0,0.0])
    ##################### END Data Collection ########################
    #The documentation is cheeks, this link has some of? the different python functions: https://github.com/xioTechnologies/Fusion/blob/main/Python/Python-C-API/Ahrs.h
    #and https://github.com/xioTechnologies/Fusion/tree/main/Python/Python-C-API should contain all the functions
    #look for PyMethodDef and PyGetSetDef 

    q = madgwick.updateMARG(qPrev, gyroscope, accelerometer, magnetometer)
    qPrev = q
    r1 = [2*(q[0]*q[0]+q[1]*q[1])-1 , 2*(q[1]*q[2]-q[0]*q[3]) , 2*(q[1]*q[3]+q[0]*q[2])]
    r2 = [2*(q[1]*q[2]+q[0]*q[3]) , 2*(q[0]*q[0]+q[2]*q[2])-1 , 2*(q[2]*q[3]-q[0]*q[1])]
    r3 = [2*(q[1]*q[3]-q[0]*q[2]) , 2*(q[2]*q[3]+q[0]*q[1]) , 2*(q[0]*q[0]+q[3]*q[3])-1]
    rotationMat = numpy.array([r1,r2,r3])
    #ahrs.update_no_magnetometer(gyroscope, accelerometer, delta_time)
    
    EFrameRaw = numpy.matmul(rotationMat, ACCVec)
    ACCmagnitudeE = math.sqrt(ACCearthFrame[0]*ACCearthFrame[0] + ACCearthFrame[1]*ACCearthFrame[1] + ACCearthFrame[2]*ACCearthFrame[2])
    ACCmagnitudeL = math.sqrt(ACCLinear[0]*ACCLinear[0] + ACCLinear[1]*ACCLinear[1] + ACCLinear[2]*ACCLinear[2])
    EarthRawMagnitude = math.sqrt(EFrameRaw[0][0]*EFrameRaw[0][0] + EFrameRaw[1][0]*EFrameRaw[1][0] + EFrameRaw[2][0]*EFrameRaw[2][0])
    RawMagnitude = math.sqrt(ACCx*ACCx + ACCy*ACCy + ACCz*ACCz)
    
    #accDataMag = ACCmagnitudeE
    sampleTime = time.time()
    
    counter1 +=1
    if counter1 > 500: #wait 10 seconds before averaging to let readings stabilize
        counter += 1
        avgMag = (RawMagnitude + avgMag*(counter-1))/counter
        
        

        
    
    if 1: #easy disable all the print statements
        if 0:                       #Change to '0' to stop  showing the angles from the gyro
            outputString +="\t# GYRX Angle %5.4f  GYRY Angle %5.4f  GYRZ Angle %5.4f # " % (gyroXangle,gyroYangle,gyroZangle)

        if 0:                       #Change to '0' to stop  showing the heading
            outputString +="\n# EulerX %5.4f  EulerY %5.4f Eulerz %5.4f#" % (euler[0],euler[1],euler[2])

        if 1:                       #Change to '0' to stop showing the acceleration
            outputString +="\n#Raw ACCx %5.4f  ACCy %5.4f  ACCz %5.4f #" % (ACCx,ACCy,ACCz)
        if 1:                       #Change to '0' to stop showing the acceleration
            outputString +="\n#Raw EarthACCx %5.4f  EarthACCy %5.4f  EarthACCz %5.4f #" % (EFrameRaw[0][0],EFrameRaw[1][0],EFrameRaw[2][0])
        if 1:                       #Change to '0' to stop showing the acceleration
            outputString +="\n# EarthACCx %5.4f  EarthACCy %5.4f  EarthACCz %5.4f #" % (ACCearthFrame[0],ACCearthFrame[1],ACCearthFrame[2])
        if 1:                       #Change to '0' to stop showing the acceleration
            outputString +="\n# LinearACCx %5.4f  LinearACCy %5.4f  LinearACCz %5.4f #" % (ACCLinear[0],ACCLinear[1],ACCLinear[2])
        if 1:                       #Change to '0' to stop showing the acceleration
            outputString +="\n# Ratio LinearACCx/ACCx %5.4f  LinearACCy/ACCy %5.4f  LinearACCz/ACCz %5.4f #" % (ACCLinear[0]/ACCx,ACCLinear[1]/ACCy,ACCLinear[2]/ACCz)
        if 1:                       #Change to '0' to stop showing the acceleration
            outputString +="\n# EarthMagnitude %5.4f  LinearMagnitude  %5.4f Earth Raw magnitude %5.4f Raw Magnitude %5.4f#" % (ACCmagnitudeE,ACCmagnitudeL,EarthRawMagnitude,RawMagnitude)
        if 1:                       #Change to '0' to stop showing the acceleration
            outputString +="\n# AvgRaw %5.5f #" % (avgMag)
        # if 1:                       #Change to '0' to stop showing the acceleration
        #     outputString +="\n# EarthACCx %5.4f  EarthACCy %5.4f  EarthACCz %5.4f #" % (EFrameAccel[0],EFrameAccel[1],EFrameAccel[2])

        print(outputString)

    
    #Make our script refresh at a consistent rate
    delTime = time.time()-lastTime
    if (delTime) < targetS:
        #print("\nSurplus time:",targetS-delTime)
        time.sleep(targetS-delTime)

    
    #EFrameAccel


