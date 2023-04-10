import serial, time
port = "/dev/ttyGSM1"
ser = serial.Serial(port, baudrate = 115200, timeout = 1) #make the timeout pretty big because it takes a second for it to open the serial channel I think
PAUSE = 0.1
print("Startup\n")

time.sleep(10.0) #Give it time to set up the multiplexing with cmux
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

    print("Waiting for cellular connection. Status:" , servStateDict[checkResult], f"({checkTime:.1f}s)", end="\r")
    
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
#Need to make a second function to just send commands since sendCheck is its own thing
