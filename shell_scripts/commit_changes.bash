#!/bin/bash
git -C /config add .
commit_message=$( date +"%Y-%m-%d-%H-%M-%S" )
git -C /config commit -m "${commit_message}"