#!/bin/bash
cd /Users/myu/projects/screenshot_syncronizer 
source venv/bin/activate
nohup python3 main.py > /dev/null 2>&1 &
