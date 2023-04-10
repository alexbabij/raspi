import serial, time
port = "/dev/ttyGSM1"
ser = serial.Serial(port, baudrate = 115200, timeout = 1) #make the timeout pretty big because it takes a second for it to open the serial channel I think
PAUSE = 0.1
print("Startup\n")
time.sleep(1.0)

GPSParams = '1,4,71'
print("\nTurning on GPS with AT+UGPS="+GPSParams)

def sendCommand(command):
    command = command + "\r\n"
    ser.write(command.encode())
    output = ser.read_until()   # default is \n
    print("Command sent:", output.rstrip().decode())     #rstrip will remove any trailing new lines or carriage return, this makes the output more readable
    response = ser.read_until()
    #response = ser.read(80)
    print("response", response.decode())
    time.sleep(PAUSE)
    return response

sendCommand('AT+UGPS='+GPSParams)
time.sleep(1.0)
gpsPResp = sendCommand('AT+UGPS?')
gpsPResp = gpsPResp.rstrip()
print(gpsPResp.decode()[7:])
#Check if the gps is turned on with our parameters
if gpsPResp.decode()[7:] != GPSParams: #there is no "7:end" in python, just leave this blank
    print("\nGPS setup failed, returned configuration of:", gpsPResp.decode())