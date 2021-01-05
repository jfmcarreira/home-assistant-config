#!/bin/bash 
mkdir -p /mnt/data
mount /dev/sda8 /mnt/data
find /mnt/data/supervisor/backup -name "*tar" -exec rm {} \;
umount /mnt/data
