#! /usr/bin/python
#Running this file will collect gps data at the specified interval 
from gps import *

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 

print(gpsd.next())