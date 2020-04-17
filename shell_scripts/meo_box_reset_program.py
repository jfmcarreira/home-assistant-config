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

meo_box_ip = sys.argv[1]
show_number = int(sys.argv[2]) 

if show_number == 0:
    cmd_sequence = ['Info', 'Right', 'OK']
if show_number < 0:
    cmd_sequence = []
    cmd_sequence.append('Left')
    for i in range(0,show_number):
        cmd_sequence.append('Left')
    cmd_sequence.append('OK')

meo_remote = pymediaroom.Remote(meo_box_ip)
loop = asyncio.get_event_loop() 
for cmd in cmd_sequence:
    loop.run_until_complete( meo_remote.send_cmd( cmd ) )
    time.sleep(1)
