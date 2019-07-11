#!/usr/bin/env python
import os, sys
import yaml
import requests
import feedparser

import smtplib
from email.mime.text import MIMEText

TESTING = True
LOCKFILE="~appsstatus.lock"

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="This script will alert you when Google services are down.")	
	parser.add_argument('-c','--config', required=True, help="""A path to a YAML configuration file with necessary 
								options specified. At a minimum this config should 
								contain a URL to the Google Apps Status RSS feed.""")
	parser.add_argument('-t','--type', choices=["continuous","statechange"], help="""Indicates whether or not an
								alert is continuous or only triggered upon state change.
								Required if not specified in config.  This flag overrides
								whatever is set in the config.""")
	parser.add_argument('-w','--whitelist', nargs='*', help="""A whitelist for which services this job should report on.
									If both this parameter and the blacklist parameter are defined,
									this whitelist parameter takes precedence and the blacklist parameter
									is ignored. If neither are defined, all Google services are monitored""") 
	parser.add_argument('-b','--blacklist', nargs='*', help="""A blacklist for which services this job should not report on.
									If both this parameter and the whitelist parameter are defined,
									the whitelist parameter takes precedence and this parameter
									is ignored. If neither are defined, all Google services are monitored""") 
	parser.add_argument('-f','--from',  help="A from address to send alerts from.")
	parser.add_argument('-a','--addresses',  type=list, nargs='*', help="A list of addresses to send alerts to.")
	parser.add_argument('-s','--smtp',  help="The SMTP host to use.")

	args = parser.parse_args()
	with open(args.config, 'r') as f:
		config = yaml.safe_load(f)

	if 'rssfeed' in config:
		rssfeed = config['rssfeed']
	else:
		sys.exit(1)

	if 'previous_state' in config:
		previous_state = config['previous_state']
	else:
		sys.exit(1)

	if 'alert_type' in config and 'type' not in args:
		alert_type = config['alert_type']
	elif 'type' in args:
		alert_type = args.type
	else:
		sys.exit(1)

	if 'whitelist' in config: 
		whitelist = config['whitelist']
	elif 'whitelist' in args:
		whitelist = args.whitelist
	else:
		sys.exit(1)

	if 'blacklist' in config: 
		blacklist = config['blacklist']
	elif 'blacklist' in args:
		blacklist = args.blacklist
	else:
		sys.exit(1)

	if whitelist and blacklist:
		blacklist = []

	if 'fromaddress' in config: 
		fromaddress = config['fromaddress']
	elif 'from' in args:
		fromaddress = args['from']
	else:
		sys.exit(1)

	if 'addressees' in config: 
		addressees = config['addressees']
	elif 'to' in args:
		fromadress = args.to
	else:
		sys.exit(1)

	if 'smtphost' in config: 
		smtphost = config['smtphost']
	elif 'smtp' in args:
		smtphost = args.smtp
	else:
		sys.exit(1)

	# Enforce concurrency of one.
	if os.path.exists(LOCKFILE):
		sys.exit(1)
	else:
		with open(LOCKFILE,"w") as f:
			f.write(str(os.getpid()))

	# Grab the current status.
	if TESTING:
		with open("test/gmailOutage.xml","r") as f:
			currentStatus = "".join(f.readlines())
	else:
		currentStatus = requests.get(rssfeed).text
	
	# Parse the current status
	newFeed = feedparser.parse(currentStatus)

	# Grab a list of alerts that we'll be sending out.
	alerts = []
	if alert_type == 'continuous' or not os.path.exists(previous_state):
		if not blacklist and not whitelist:
			alerts = newFeed.entries
		elif whitelist:
			while newFeed.entries:
				newEntry = newFeed.entries.pop()
				if newEntry.title in whitelist:
					alerts.append(newEntry)
		elif blacklist:
			while newFeed.entries:
				newEntry = newFeed.entries.pop()
				if newEntry.title not in blacklist:
					alerts.append(newEntry)
	else:
		oldFeed = feedparser.parse(previous_state)
		# For detecting state transition.
		if not oldFeed.entries:
			if not blacklist and not whitelist:
				alerts = newFeed.entries
			elif whitelist:
				while newFeed.entries:
					newEntry = newFeed.entries.pop()
					if newEntry.title in whitelist:
						alerts.append(newEntry)
			elif blacklist:
				while newFeed.entries:
					newEntry = newFeed.entries.pop()
					if newEntry.title not in blacklist:
						alerts.append(newEntry)
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
	with open(previous_state,"w") as f:
		f.write(currentStatus)

	for alert in alerts:
		msg = MIMEText(alert.summary, 'html', 'utf-8')
		msg['Subject'] = "G Suite Status Alert: %s" % alert.title
		msg['From'] = fromaddress
		msg['To'] = ", ".join(addressees)

		s = smtplib.SMTP(smtphost)
		s.sendmail(fromaddress, addressees, msg.as_string())
		s.quit()

	os.remove(LOCKFILE)
