import subprocess
subprocess.Popen(["./run_cgps.sh"],start_new_session=True)
subprocess.Popen(["python","collect_gpsdata.py"],start_new_session=True)
#This is the workaround for one of the most annoying and impossible to troubleshoot issues out there that I won't even get into
print("\nEnd Setup")