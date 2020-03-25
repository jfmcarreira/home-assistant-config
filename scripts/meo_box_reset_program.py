# Script to reset the current show on MEO box.
# 
# The first input argument in the BOX IP
#
# This work uses the pymediaroom package
# https://github.com/dgomes/pymediaroom


import pymediaroom
import sys
import asyncio
import time

# Reset show cmd sequence
# This is the button combination required to reset the show
cmd_sequence = ['Info', 'Right', 'OK']

meo_box_ip = sys.argv[1]
meo_remote = pymediaroom.Remote(meo_box_ip)
loop = asyncio.get_event_loop() 
for cmd in cmd_sequence:
    loop.run_until_complete( meo_remote.send_cmd( cmd ) )
    time.sleep(1)
