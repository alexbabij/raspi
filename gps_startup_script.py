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
    time.sleep(PAUSE) # basically wait to send the next command


sendCommand("AT+UCGED?")
sendCommand("AT+UCGED?")