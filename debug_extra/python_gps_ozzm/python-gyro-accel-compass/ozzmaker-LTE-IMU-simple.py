#!/usr/bin/python
#
#       This is the base code needed to get usable angles from the IMU on
#       the  OzzMaker SARA-R5 LTE-M GPS + 10DOF baord using a Complementary filter.
#       The readings can be improved by adding more filters, E.g Kalman,
#       Low pass, median filter, etc.. See ozzmaker-LTE-IMU.py for more advanced code.
#
#       Feel free to do whatever you like with this code.
#       Distributed as-is; no warranty is given.
#
#       https://ozzmaker.com/


import time
import math
import IMU
import datetime




RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.0175 #500 dps
#G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40      # Complementary filter constant
mRes = 1.0/16384.0
MMC5983MA_offset = 131072.0

################# Compass Calibration values ############
# Use calibrate-ozzmaker-LTE-IMU.py to get calibration values
# Calibrating the compass isnt mandatory, however a calibrated
# compass will result in a more accurate heading values.



magXmin = 0
magYmin = 0
magZmin = 0
magXmax = 0
magYmax = 0
magZmax = 0

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


IMU.detectIMU()     #Detect if OzzMaker SARA-R5 LTE-M GPS + 10DOF is connected.
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass


a = datetime.datetime.now()



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

    MAGx  = MAGx * (1.0/16384.0)  #18 bits
    MAGy  = MAGy * (1.0/16384.0)  #18 bits
    MAGz  = MAGz * (1.0/16384.0)  #18 bits


    ##Calculate loop Period(LP). How long between Gyro Reads
    b = datetime.datetime.now() - a
    a = datetime.datetime.now()
    LP = b.microseconds/(1000000*1.0)
    outputString = "Loop Time %5.2f " % ( LP )


    #Convert Gyro raw to degrees per second
    rate_gyr_x =  GYRx * G_GAIN
    rate_gyr_y =  GYRy * G_GAIN
    rate_gyr_z =  GYRz * G_GAIN


    #Calculate the angles from the gyro.
    gyroXangle+=rate_gyr_x*LP
    gyroYangle+=rate_gyr_y*LP
    gyroZangle+=rate_gyr_z*LP


    #Convert Accelerometer values to degrees
    AccXangle =  (math.atan2(ACCy,ACCz)*RAD_TO_DEG)
    AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG

    #convert the values to -180 and +180
    if AccYangle > 90:
        AccYangle -= 270.0
    else:
        AccYangle += 90.0



    #Complementary filter used to combine the accelerometer and gyro values.
    CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
    CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle

    #Calculate heading
    heading = 180 * math.atan2(MAGy,MAGx)/M_PI

    #Only have our heading between 0 and 360
    if heading < 0:
        heading += 360

    ####################################################################
    ###################Tilt compensated heading#########################
    ####################################################################
    #Flip Z for tilt compesnation to work.
    MAGz = -MAGz

    #Normalize accelerometer raw values.
    accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
    accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)


    #Calculate pitch and roll
    pitch = math.asin(accXnorm)
    roll = -math.asin(accYnorm/math.cos(pitch))


    #Calculate the new tilt compensated values
    #X compensation
    magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)

    #Y compensation
    magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)


    #Calculate tilt compensated heading
    tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI

    if tiltCompensatedHeading < 0:
        tiltCompensatedHeading += 360


    ##################### END Tilt Compensation ########################


    if 1:                       #Change to '0' to stop showing the angles from the accelerometer
        outputString += "#  ACCX Angle %5.2f ACCY Angle %5.2f  \n#  " % (AccXangle, AccYangle)
    if 1:                       #Change to '0' to stop showing the angles from the accelerometer
        outputString += "#  GYRx Raw %5.6f GYRy Raw %5.6f GYRz Raw %5.6f \n#  " % (rate_gyr_x, rate_gyr_y, rate_gyr_z)
    if 1:                       #Change to '0' to stop showing the angles from the accelerometer
        outputString += "#  ACCx Raw %5.2f ACCy Raw %5.2f ACCz Raw %5.2f \n#  " % (ACCx, ACCy, ACCz)

    if 1:                       #Change to '0' to stop  showing the angles from the gyro
        outputString +="\t# GRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f # " % (gyroXangle,gyroYangle,gyroZangle)

    if 1:                       #Change to '0' to stop  showing the angles from the complementary filter
        outputString +="\t#  CFangleX Angle %5.2f   CFangleY Angle %5.2f  #" % (CFangleX,CFangleY)

    if 1:                       #Change to '0' to stop  showing the heading
        outputString +="\t# HEADING %5.2f  tiltCompensatedHeading %5.2f #" % (heading,tiltCompensatedHeading)


    print(outputString)



    #slow program down a bit, makes the output more readable
    time.sleep(0.03)
