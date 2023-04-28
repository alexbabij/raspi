import serial, time
import subprocess
port = "/dev/ttyGSM1"
ser = serial.Serial(port, baudrate = 115200, timeout = 1) #make the timeout pretty big because it takes a second for it to open the serial channel I think
PAUSE = 0.1
print("Startup\n")

#time.sleep(10.0) #Give it time to set up the multiplexing with cmux
#Start by running our multipex configuration script

with open("initialize_multiplex.py") as f:
    exec(f.read())

print("\n")

servStateDict = {'0': 'not known or not detectable', '1': 'radio off', '2': 'searching', '3': 'no service', '4': 'registered', '5': "string parsing or other error"}
def sendCheck(command):
    command = command + "\r\n" #\r is carriage return which I think signals the end of the command
    ser.write(command.encode()) #.write sends the command over the serial port "ser"
    #ser.flush()
    #rstrip will remove any trailing new lines or carriage return from what we just sent, this makes the output more readable
    response = ser.read_until(b'OK')
    #response = ser.read(80) #This would read UP TO 80 bytes at which point it will stop, or it will stop if it reaches the timeout period before collecting 80 bytes
    respString = response.decode()
    with open("startup_log.txt", "w") as f: #save our output to a log file
        f.write(repr(respString))
    startPos = respString.find("+UCGED: ") #starting position of response string (read_until doesnt clear the serial buffer, so running it twice in a row will detect our input twice)
    
    if len(respString) > startPos+13: #If the string is too short i.e. from returning no value or "ERROR", we just say it has no connection with 0, instead of the script erroring out
        servState = respString[startPos+13]
    else:
        servState = '0'
    
    if servState not in servStateDict: #If its still brokey we just say so 
        servState = '5'

    time.sleep(PAUSE) # basically wait to send the next command
    return servState




#Starting agps setup, first, checking to wait for a valid cellular connection 
checkResult = '0'
checkTime = 0
checkTime5 = 6

while checkResult != '4':
    print('\r', end='') #clear the previous line
    print("Waiting for cellular connection. Status:" , servStateDict[checkResult], f"({checkTime:.1f}s)")
    
    if checkTime5 >= 7:
        checkResult = sendCheck("AT+UCGED?")
        checkTime += PAUSE #running the function adds time (by design) so we actually need to include this
        checkTime5 = 0 
    
    checkTime5 += 1
    checkTime += 1
    time.sleep(1.0)

    if checkTime >= 240:
        print("Timeout no connection")
        break
    
print("\nReady, running assisted GPS setup\n")

time.sleep(1.0)
with open("initialize_agps.py") as f:
    exec(f.read())
#Running them like this doesnt check if they were truly successful, they just probably will be, but there is no actual check

time.sleep(1.0)

GPSParams = '1,4,71'
print("\nTurning on GPS with AT+UGPS="+GPSParams)

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

sendCommand('AT+UGPS='+GPSParams)
time.sleep(7.0)
ser.read_all()
gpsPResp = sendCommand('AT+UGPS?')
gpsPResp = gpsPResp.rstrip()
#Check if the gps is turned on with our parameters
if gpsPResp.decode()[7:] == GPSParams: #there is no "7:end" in python, just leave this blank
    print("Success")
else:
    print("\nGPS setup failed, returned configuration of:", gpsPResp.decode())

ser.read_all() #should do basically the same as flushing the buffer
time.sleep(1.0)
#Enable communication betweenn GPS and GSM by turning on unsolicited aiding 

sendCommand("AT+UGIND=1") #If this fails our gps will just not work through gpsd, so we will retry it once (might make it retry n times idk)
time.sleep(3.0)
ser.read_all()
gpsPResp = sendCommand('AT+UGIND?') # I really should stop switching between ' and " randomly
gpsPResp = gpsPResp.rstrip()
#Check if the gps is set with our parameters
if gpsPResp.decode()[8:] == '1': #there is no "7:end" in python, just leave this blank
    print("\nSuccess")
else:
    print("\nSetup failed, returned configuration of:", gpsPResp.decode()[8])
    sendCommand("AT+UGIND=1")



#Configure gps settings including update rate
with open('configDevice.txt') as mycfgfile:
    config = mycfgfile.read().splitlines() #Read in each line as a list i.e. [a:1, b:2]
    config.pop(0)
    config = dict([eachLine.split(":") for eachLine in config]) #Split by ":" and turn into dict

print("\n")
updateRate = int(config["updateRate"]) #in Hz 
#It doesn't matter that we can't configure an updateRate that is not an integer i.e. 1.1Hz because we can't just generate the corresponding binary command anyway
#With our specific gps, with a baud rate of 38400, 10Hz may be unstable idk
#contains binary strings that must be sent to set each of the different update rates
#binary stuff is stored as a string since that is the format we will use when we send it
updateRDict = {1: 'B5 62 06 08 06 00 E8 03 01 00 01 00 01 39', 2: 'B5 62 06 08 06 00 F4 01 01 00 01 00 0B 77', 4: 'B5 62 06 08 06 00 FA 00 01 00 01 00 10 96',
5: 'B5 62 06 08 06 00 C8 00 01 00 01 00 DE 6A', 8: 'B5 62 06 08 06 00 7D 00 01 00 01 00 93 A8', 10: 'B5 62 06 08 06 00 64 00 01 00 01 00 7A 12'}
#These came from the u-center software on windows that can generate the binary with the checksum for changing different settings on M8 gps'
#Normally, gpsd can do this for us and send binary directly to the gps, but since we have to communicate over AT commands because
#our gps goes through the cellular module on the ublox SARA-R5-M8, we have to do it ourselves.

#Default update rate is 1 on gps boot, so if we have it set to 1 in here, do nothing
#We also don't want to send an incomplete binary string somehow i.e. AT+UGUBX="wrong"
if (updateRate != 1) & (updateRate in updateRDict):
    sendCommand("AT+UGUBX=\""+updateRDict[updateRate]+"\"")
    print('setting update rate to: '+str(updateRate)+"Hz")
else:
    print("Invalid or already set update rate")

# time.sleep(1.0)
# print('configuring dynamic model')
# #contains ubx binary strings for different vehicle model configurations
# modelDict = {'automotive': 'B5 62 06 24 24 00 FF FF 04 03 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 10 27 00 00 00 00 00 00 00 00 4B 97',
# 'portable': 'B5 62 06 24 24 00 FF FF 00 03 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 10 27 00 00 00 00 00 00 00 00 47 0F'}
# #automotive
# sendCommand("AT+UGUBX=\""+modelDict['automotive']+"\"")

subprocess.Popen(["./run_cgps.sh"],start_new_session=True)
#subprocess.Popen(["python","collect_gpsdata.py"],start_new_session=True)
#This is the workaround for one of the most annoying and impossible to troubleshoot issues out there that I won't even get into
print("\nEnd Setup")