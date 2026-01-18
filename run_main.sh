#!/bin/bash
echo "----- Job started at $(date)" >> /Users/marlene/CalendarSync/run.log
cd /Users/marlene/CalendarSync  || exit
/Users/marlene/CalendarSync/.venv/bin/python main.py
echo "py-script run completed at $(date)" >> /Users/marlene/CalendarSync/run.log

git add calendar.ics
git commit -m "Update calendar $(date '+%Y-%m-%d %H:%M')"
git push origin main
echo "github push completed at $(date)" >> /Users/marlene/CalendarSync/run.log
