#!/bin/bash
#eval "$(ssh-agent -s)"
#ssh-add ~/.ssh/id_ed25519

# BASH VARS
WDIR="/Users/marlene/CalendarSync"
PYTHON_PATH="$WDIR/.venv/bin/python"
LOGFILE="$WDIR/run.log"

echo "----- Job started at $(date) -----" >> "$LOGFILE"

# SET WDR
cd "$WDIR"  || exit

# RUN PYTHON
"$PYTHON_PATH" main.py --view 26V1
"$PYTHON_PATH" main.py --view 26V2
echo "py-script run completed at $(date)" >> "$LOGFILE"

# ADD TO GIT
git add termine_26V1.ics
git add termine_26V1.json
git add termine_26V2.ics
git add termine_26V2.json
git commit -m "Update calendar $(date '+%Y-%m-%d %H:%M')"  >> "$LOGFILE" 

# push to repo
git push origin main >> "$LOGFILE" 
echo "github push completed at $(date) " >> "$LOGFILE"
echo "-------------------------------- " >> "$LOGFILE"
