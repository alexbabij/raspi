#!/usr/bin/env python
import serial, time

# print("Hello World")
# output="klajhd\t\n"
# print(output)
# a=output.rstrip()
# print(a)


# b = output.encode()
# print(b)

# print(b.decode().rstrip())



# output = ser.read_until(b'OK')
# print(b.decode())


# #AT+UCGED?: output: 
# # +UCGED: 2
# # 6,0,001,01
# # 2525,5,25,50,2b67,69f6bc7,111,0000
# # 0000,ffff,ff,67,19,0.00,255,255,255,
# # 67,11,255,0,255,255,0,0,0
# # OK

#b'AT+UCGED?\r\r\n+UCGED: 2\r\n6,4,fff,fff\r\n5110,13,50,50,ffff,0000000,254,d0fafd59,ff49,b1,27,15,0.50,1,255,255,28,255,255,0,255,255,0\r\n\r\nOK'

#Make a dictionary for each of the potential outputs we can get for the response we are reading 
servStateDict = {'0': 'not known or not detectable', '1': 'radio off', '2': 'searching', '3': 'no service', '4': 'registered'}

port = "/dev/ttyGSM1"
ser = serial.Serial(port, baudrate = 115200, timeout = 1) #make the timeout pretty big because it takes a second for it to open the serial channel I think
PAUSE = 0.1
 
def sendCommand(command):
    command = command + "\r\n" #\r is carriage return which I think signals the end of the command
    ser.write(command.encode()) #.write sends the command over the serial port "ser"
    #ser.flush()
    cmdSent = ser.read_until('\n')   # default is \n
    print("Command sent:", cmdSent.rstrip().decode())     #rstrip will remove any trailing new lines or carriage return from what we just sent, this makes the output more readable
    response = ser.read_until(b'OK')
    #response = ser.read(80) #This would read UP TO 80 bytes at which point it will stop, or it will stop if it reaches the timeout period before collecting 80 bytes
    print("response", response.decode())
    respString = response.decode()
    startPos = respString.find("\n+UCGED: ") #starting position of response string (read_until doesnt clear the serial buffer, so running it twice in a row will detect our input twice)
    servState = respString[startPos+14]
    print("Radio Service State:",servState+":",servStateDict[servState])
    time.sleep(PAUSE) # basically wait to send the next command


sendCommand("AT+UCGED?")
#+UCGED: 2\r\n6,4
