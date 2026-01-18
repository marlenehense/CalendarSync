#!/bin/bash
echo "----- Job started at $(date)" >> /Users/marlene/CalenderSync/run.log
cd /Users/marlene/CalenderSync  || exit
/Users/marlene/CalenderSync/.venv/bin/python main.py
echo "Script run completed at $(date)" >> /Users/marlene/CalenderSync/run.log
