# FatFingerHelperBot
/u/FatFingerHelperBot on Reddit

## Overview
### MobileLinkHelperBot.py
The main bot code. This script will monitor /r/all and detect valid comments that contain link display strings of <= 3 characters. The bot will reply to any such comments, providing a longer display string for any links that were too short in order to make them more easily tappable for users of mobile Reddit client apps. 
### MobileLinkHelperMailMonitor.py
This script enables the "message to delete" functionality. It listens to the bot's inbox, detects messages with the body "delete {ID_HERE}," and deletes the offending comment as long as the message's author is the same as the parent comment's author.
