#!/bin/bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

LOGFILE="/Users/marlene/CalenderSync/run.log"


echo "----- Job started at $(date)" >> "$LOGFILE"
cd /Users/marlene/CalendarSync  || exit
/Users/marlene/CalendarSync/.venv/bin/python main.py
echo "py-script run completed at $(date)" >> "$LOGFILE"

git add calendar.ics
git add run.log
git commit -m "Update calendar $(date '+%Y-%m-%d %H:%M')"  >> "$LOGFILE" 2>&1
git push origin main
echo "github push completed at $(date)" >> "$LOGFILE"
