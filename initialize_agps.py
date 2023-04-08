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
 
 
'''
sendCommand("AT+CFUN=0")                                #Turn off radio
time.sleep(2)
sendCommand("AT+CGDCONT=1,\"IP\",\"hologram\"")         #Set the APN for network operator
time.sleep(2)
sendCommand("AT+CFUN=1")                                #Turn on radio
'''#Should be unnessecary.
time.sleep(2)
#sendCommand("AT+CGACT=1,1") #Should be unnessecary?
time.sleep(2)
sendCommand("AT+UPSD=0,0,0")                            #Set the PDP type to IPv4
time.sleep(2)
sendCommand("AT+UPSD=0,100,1")                          #Profile #0 is mapped on CID=1
time.sleep(2)
sendCommand("AT+UPSDA=0,3")                             #Activate the PSD profile
time.sleep(2)
#sendCommand("AT+UGPS=1,4,67")  #Start the GNSS with GPS+SBAS+GLONASS systems and local aiding.
 
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