#! /usr/bin/python

import subprocess
#This runs cgps in a separate python script that autoruns so it doesnt put stuff in the terminal window
#We can also change this through github since its in raspi/

subprocess.Popen(['/bin/bash', './run_cgps.sh'],start_new_session=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print('running cpgs :(')