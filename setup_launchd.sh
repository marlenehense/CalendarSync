#!/bin/bash

# create symbolic link to launchd default dir via:
ln -s ~/CalendarSync/com.marlene.calendarsync.plist  ~/Library/LaunchAgents/com.marlene.calendarsync.plist

#launch the job
launchctl load ~/Library/LaunchAgents/com.marlene.calendarsync.plist