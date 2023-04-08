#!/usr/bin/env python
import serial, time
 
port = "/dev/ttyGSM1"
PAUSE = 0.1
 
def sendCommand(command):
    command = command + "\r\n"
    ser.write(command.encode())
    #ser.flush()
    output = ser.read_until()   # default is \n
    print("Command sent:", output.rstrip())     #rstrip will remove any trailing new lines or carriage return, this makes the output more readable
    response = ser.read_until()
    #response = ser.read(80)
    print("response", response)
    time.sleep(PAUSE)
 
ser = serial.Serial(port, baudrate = 9600, timeout = 0.2)
 
 
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
 
time.sleep(PAUSE+3)
 
 
 
sendCommand("AT")