import serial, time
port = "/dev/ttyGSM1"
ser = serial.Serial(port, baudrate = 115200, timeout = 1) #make the timeout pretty big because it takes a second for it to open the serial channel I think
PAUSE = 0.1
print("Startup\n")


def sendCommand(command,readall=False): #optional function input for timeout
    command = command + "\r\n"
    ser.write(command.encode())
    output = ser.read_until(b'\n')   # default is \n
    print("Command sent:", output.rstrip().decode())     #rstrip will remove any trailing new lines or carriage return, this makes the output more readable
    if readall == False:
        response = ser.read_until(b'\n')
    else:
        response = ser.read_all()
    #response = ser.read(80)
    print("response", response.decode())
    time.sleep(PAUSE)
    return response

print("sending command")
##portable:
#sendCommand("AT+UGUBX=\"B5 62 06 24 24 00 FF FF 00 02 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 10 27 00 00 00 00 00 00 00 00 46 EE\"")
#update rate 5hz? idk maybe 2 
#sendCommand("AT+UGUBX=\"B5 62 06 08 06 00 F4 01 01 00 01 00 0B 77\"")
##STationary 2d only
#sendCommand("AT+UGUBX=\"B5 62 06 24 24 00 FF FF 02 01 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 10 27 00 00 00 00 00 00 00 00 47 11\"")
sendCommand("AT+UGUBX=\"B5 62 06 24 24 00 FF FF 08 03 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 10 27 00 00 00 00 00 00 00 00 4F 1F\"")


print("\nEnd Setup")