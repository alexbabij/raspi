#!/usr/bin/env python
import serial, time
 
port = "/dev/ttyGSM2"
PAUSE = 0.1
 
def sendCommand(command):
    command = command + "\r\n"
    ser.write(command)
    #ser.flush()
    output = ser.read_until()   # default is \n
    print("Command sent:", output.rstrip())     #rstrip will remove any trailing new lines or carriage return, this makes the output more readable
    response = ser.read_until()
    #response = ser.read(80)
    print("response", response)
    time.sleep(PAUSE)
 
ser = serial.Serial(port, baudrate = 115200, timeout = 0.2)
 
 
sendCommand("AT+UGPRF=2")               #Configure multiplexer
sendCommand("AT+USIO=2")                #Configure serial interface varient
 
 
 
#Activate storing of last values of selected NMEA sentences from the GPS module
sendCommand("AT+UGGLL=1")               #Activate storing of last value of $GLL
sendCommand("AT+UGGSV=1")               #Activate storing of last value of $GSV
sendCommand("AT+UGGGA=1")               #Activate storing of last value of $GGA
sendCommand("AT+UGRMC=1")               #Activate storing of last value of $RMC
 
#Ennable communication betweenn GPS and GSM
sendCommand("AT+UGIND=1")               #Activate the unsolicited aiding result
 
 
''''
AT+UGPS=[mode],[aid_mode],[GNSS_systems]
[mode]
 0 : Off
 1 : On
[aid_mode]
 0 (default value): no aiding
 1: automatic local aiding
 2: AssistNow Offline
 4: AssistNow Online
 8: AssistNow Autonomou'
[GNSS_systems]
 1: GPS
 2: SBAS
 4: Galileo
 8: BeiDo
 16: IMES
 32: QZSS
 64: GLONAS
 Examples;
 AT+UGPS=1,0,64         Turn on GNSS with no aiding and only use GLONASS
 AT+UGPS=0              Turn off GNSS
 AT+UGPS=1,2,67         Start the GNSS with GPS+SBAS+GLONASS systems and AssistNow Offline aiding
'''
#Turn on GNSS
sendCommand("AT+UGPS=1,1,67")  #Start the GNSS with GPS+SBAS+GLONASS systems and local aiding.
 
'''
The above command will response with a response code indicating if there were any errors.
UUGIND: [aid_mode],[result]
[RESULT]
 0: No error
 1: Wrong URL (for AssistNow Offline)
 2: HTTP error (for AssistNow Offline)
 3: Create socket error (for AssistNow Online)
 4: Close socket error (for AssistNow Online)
 5: Write to socket error (for AssistNow Online)
 6: Read from socket error (for AssistNow Online)
 7: Connection/DNS error (for AssistNow Online)
 8: File system error
 9: Generic error
 10: No answer from GNSS (for local aiding and AssistNow Autonomous)
 11: Data collection in progress (for local aiding)
 12: GNSS configuration failed (for AssistNow Autonomous)
 13: RTC calibration failed (for local aiding)
 14: feature not supported (for AssistNow Autonomous)
 15: feature partially supported (for AssistNow Autonomous)
 16: authentication token missing (required for aiding for u-blox M8 and future versions)
'''
 
time.sleep(PAUSE+3)
 
 
 
sendCommand("AT")