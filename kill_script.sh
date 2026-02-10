#!/bin/bash
pkill -f SysAudioDaemon
pkill -f SysInputHelper
pkill -f "main.py"
echo "Processes terminated"