import serial, time
port = "/dev/ttyGSM1"
ser = serial.Serial(port, baudrate = 115200, timeout = 1) #make the timeout pretty big because it takes a second for it to open the serial channel I think
PAUSE = 0.1
print("Startup\n")
time.sleep(1.0)

GPSParams = '1,4,71'
print("\nTurning on GPS with AT+UGPS="+GPSParams)

def sendCommand(command,timeout=1): #optional function input for timeout
    command = command + "\r\n"
    ser.write(command.encode())
    output = ser.read_until('\n')   # default is \n
    print("Command sent:", output.rstrip().decode())     #rstrip will remove any trailing new lines or carriage return, this makes the output more readable
    response = ser.read_until('\n',timeout)
    #response = ser.read(80)
    print("response", response.decode())
    time.sleep(PAUSE)
    return response

sendCommand('AT+UGPS='+GPSParams,timeout=3)
time.sleep(5.0)
gpsPResp = sendCommand('AT+UGPS?')
gpsPResp = gpsPResp.rstrip()
#Check if the gps is turned on with our parameters
if gpsPResp.decode()[7:] == GPSParams: #there is no "7:end" in python, just leave this blank
    print("Success")
else:
    print("\nGPS setup failed, returned configuration of:", gpsPResp.decode())

time.sleep(3.0)
#Enable communication betweenn GPS and GSM by turning on unsolicited aiding 
sendCommand("AT+UGIND=1")
