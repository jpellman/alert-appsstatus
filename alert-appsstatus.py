#!/usr/bin/env python
import os, sys
import requests
import feedparser

import smtplib
from email.mime.text import MIMEText

# Put me in a config file.
RSSFEED = "https://www.google.com/appsstatus/rss/en"
CONTINUOUS_ALERTS = False
PREVIOUS_STATE = "lastStatus.xml"
WHITELIST = []
FROMADDRESS = "noreply@zombo.com"
ADDRESSEES = ["faketest@user.com"]
SMTPHOST = "localhost"

LOCKFILE="~appsstatus.lock"

# Enforce concurrency of one.
if os.path.exists(LOCKFILE):
	sys.exit(1)
else:
	with open(LOCKFILE,"w") as f:
		f.write(str(os.getpid()))

# Grab the current status.
#currentStatus = requests.get(RSSFEED).text
# For testing
with open("test/gmailOutage.xml","r") as f:
	currentStatus = "".join(f.readlines())

# Parse the current status
newFeed = feedparser.parse(currentStatus)

# Grab a list of alerts that we'll be sending out.
alerts = []
if CONTINUOUS_ALERTS or not os.path.exists(PREVIOUS_STATE):
	alerts = newFeed.entries
else:
	oldFeed = feedparser.parse(PREVIOUS_STATE)
	# For detecting state transition.
	if not oldFeed.entries:
		alerts = newFeed.entries
	else:
		while newFeed.entries:
			newEntry = newFeed.entries.pop()
			for idx, oldEntry in enumerate(oldFeed.entries):
				'''
				If this entry has been seen before- do not add to the alerts list 
				and remove from list of potential comparisons.  Otherwise,
				add it to the list of alerts to send out.
				'''
				if (newEntry.published == oldEntry.published) and (newEntry.title == oldEntry.title) and (newEntry.updated == oldEntry.updated):
					del oldFeed.entries[idx]
				else:
					alerts.append(newEntry)
	with open(PREVIOUS_STATE,"w") as f:
		f.write(currentStatus)

for alert in alerts:
	msg = MIMEText(alert.summary, 'html', 'utf-8')
	msg['Subject'] = "G Suite Status Alert: %s" % alert.title
	msg['From'] = FROMADDRESS
	msg['To'] = ", ".join(ADDRESSEES)

	s = smtplib.SMTP(SMTPHOST)
	s.sendmail(FROMADDRESS, ADDRESSEES, msg.as_string())
	s.quit()

os.remove(LOCKFILE)
