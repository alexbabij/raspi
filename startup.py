import serial, time
port = "/dev/ttyGSM1"
ser = serial.Serial(port, baudrate = 115200, timeout = 1) #make the timeout pretty big because it takes a second for it to open the serial channel I think
PAUSE = 0.1
 
def sendCheck(command):
    command = command + "\r\n" #\r is carriage return which I think signals the end of the command
    ser.write(command.encode()) #.write sends the command over the serial port "ser"
    #ser.flush()
    #rstrip will remove any trailing new lines or carriage return from what we just sent, this makes the output more readable
    response = ser.read_until(b'OK')
    #response = ser.read(80) #This would read UP TO 80 bytes at which point it will stop, or it will stop if it reaches the timeout period before collecting 80 bytes
    respString = response.decode()
    startPos = respString.find("+UCGED: ") #starting position of response string (read_until doesnt clear the serial buffer, so running it twice in a row will detect our input twice)
    servState = respString[startPos+13]
    time.sleep(PAUSE) # basically wait to send the next command
    return servState


checkResult = '0'
checkTime = 0
checkTime5 = 100

while checkResult != '4':

    print(f"Waiting for cellular connection ({checkTime:.1f}s)", end="\r")
    
    if checkTime5 >= 7:
        checkResult = sendCheck("AT+UCGED?")
        checkTime += PAUSE*2 #running the function adds time (by design) so we actually need to include this
        checkTime5 = 0 
    
    checkTime5 += 1
    checkTime += 1
    time.sleep(1.0)

    if checkTime >= 120:
        print("Timeout no connection")
        break
    
print("Ready")