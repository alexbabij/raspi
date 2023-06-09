#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0
 
import os
from gps import *
from time import *
import time
import threading

#Change the refresh rate here to match one from the gps. compare gpsd time readings with if statement and if they are the same,
#wait to run again by + 1/2 *Hz so that we can get closer to middle of readings
 
gpsd = None #seting the global variable
 
os.system('clear') #clear the terminal (optional)
 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    global elapsed
    while gpsp.running:
      start = time.time()
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
      end = time.time()
      elapsed = (end-start)
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start() # start it up
    while True:
      #It may take a second or two to get good data
      #print gpsd.fix.latitude,', ',gpsd.fix.longitude,'  Time: ',gpsd.utc
 
      os.system('clear')
 
      print("\n")
      print(' GPS reading')
      print('----------------------------------------')
      print('latitude    ' , gpsd.fix.latitude)
      print('longitude   ' , gpsd.fix.longitude)
      print('time utc    ' , gpsd.utc,' + ', gpsd.fix.time)
      print('altitude (m)' , gpsd.fix.altitude)
      print('eps         ' , gpsd.fix.eps)
      print('epx         ' , gpsd.fix.epx)
      print('epv         ' , gpsd.fix.epv)
      print('ept         ' , gpsd.fix.ept)
      print('speed (m/s) ' , gpsd.fix.speed)
      print('climb       ' , gpsd.fix.climb)
      print('track       ' , gpsd.fix.track)
      print('mode        ' , gpsd.fix.mode)
      print("\n")
      print('Time/refresh',elapsed)
      print('\n')
      print('sats        ' , gpsd.satellites)
 
      time.sleep(0.1) #set to whatever
 
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nKilling Thread...")
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print("Done.\nExiting.")