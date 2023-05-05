#! /usr/bin/python
#Instead of trying to get subprocess to do what I want, just put everything in main which is I think the more correct way to do this.
import subprocess


#Run startup script
print('Main: Running startup')
import startup
startup
print('running cpgs :(')
#subprocess.Popen(["./run_cgps.sh"],start_new_session=True)
#subprocess.Popen(["python","collect_gpsdata.py"],start_new_session=True)
#This is the workaround for one of the most annoying and impossible to troubleshoot issues out there that I won't even get into
#I think the issue revolves around gpsd "giving up" the serial channel ttyGSM3 after it has previously claimed it
#running cgps in the background constantly means that gpsd never "releases" the channel

print('Main: Data collection setup')
import setup_data_collection #All this really "sets up" is making us wait until we have a gps fix
setup_data_collection

print('Main: Starting data collection')
import collect_gpsdata
collect_gpsdata
