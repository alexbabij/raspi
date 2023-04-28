#! /usr/bin/python
#Instead of trying to get subprocess to do what I want, just put everything in main which is I think the more correct way to do this.

#Run startup script
print('Main: Running startup')
import startup
startup

print('Main: Data collection setup')
import setup_data_collection #All this really "sets up" is making us wait until we have a gps fix
setup_data_collection

print('Main: Starting data collection')
import collect_gpsdata
collect_gpsdata
