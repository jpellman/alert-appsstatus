#!/usr/bin/env python
import os, sys
import yaml
import requests
import feedparser
import psutil

import smtplib
from email.mime.text import MIMEText

def statusLock(pidfile):
	# Enforce concurrency of one.
	if os.path.exists(pidfile):
                try:
                    with open(pidfile,"r") as f:
                            oldpid = int(f.read().strip())
                    # If pidfile is stale overwrite it.
                    if oldpid in psutil.pids():
		        sys.exit(1)
                    else:
    		        with open(pidfile,"w") as f:
			    f.write(str(os.getpid()))
                except:
		    sys.exit(1)
	else:
		with open(pidfile,"w") as f:
			f.write(str(os.getpid()))

def statusUnlock(pidfile):
	os.remove(pidfile)

def compareStatus(currentStatus,previousStatus,alertType,alertFilter,blacklist):
	# Parse the current status
	newFeed = feedparser.parse(currentStatus)

	# Grab a list of alerts that we'll be sending out.
	alerts = []
	if alertType == 'continuous' or not os.path.exists(previousStatus):
		if not alertFilter:
			alerts = newFeed.entries
		elif not blacklist:
			while newFeed.entries:
				newEntry = newFeed.entries.pop()
				if newEntry.title in alertFilter:
					alerts.append(newEntry)
		elif blacklist:
			while newFeed.entries:
				newEntry = newFeed.entries.pop()
				if newEntry.title not in alertFilter:
					alerts.append(newEntry)
	else:
		oldFeed = feedparser.parse(previousStatus)
		# For detecting state transition.
		if not oldFeed.entries:
			if not alertFilter:
				alerts = newFeed.entries
			elif not blacklist:
				while newFeed.entries:
					newEntry = newFeed.entries.pop()
					if newEntry.title in alertFilter:
						alerts.append(newEntry)
			elif blacklist:
				while newFeed.entries:
					newEntry = newFeed.entries.pop()
					if newEntry.title not in alertFilter:
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
	with open(previousStatus,"w") as f:
		f.write(currentStatus)
        return alerts

def sendAlerts(alerts):
	for alert in alerts:
		msg = MIMEText(alert.summary, 'html', 'utf-8')
		msg['Subject'] = "G Suite Status Alert: %s" % alert.title
		msg['From'] = fromaddress
		msg['To'] = ", ".join(addressees)

		s = smtplib.SMTP(smtphost)
		s.sendmail(fromaddress, addressees, msg.as_string())
		s.quit()

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
	parser.add_argument('-p','--pidfile',  help="""Where to place the pidfile.  
                                                The pidfile is used to ensure that only one copy of this script is running at a time.
                                                This is a crude form of mutual exclusion.""")

	args = parser.parse_args()
	with open(args.config, 'r') as f:
		config = yaml.safe_load(f)

	if 'rssfeed' in config:
		rssfeed = config['rssfeed']
	else:
		sys.exit(1)

	if 'previousStatus' in config:
		previousStatus = config['previousStatus']
	else:
		sys.exit(1)

	if 'alertType' in config and 'type' not in args:
		alertType = config['alertType']
	elif 'type' in args:
		alertType = args.type
	else:
		sys.exit(1)

        blacklist = False
	if 'whitelist' in config: 
		alertFilter = config['whitelist']
	elif 'whitelist' in args:
		alertFilter = args.whitelist
	elif 'blacklist' in config: 
		alertFilter = config['blacklist']
                blacklist = True
	elif 'blacklist' in args:
		alertFilter = args.blacklist
                blacklist = True
	else:
		alertFilter = []

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

	if 'pidfile' in config: 
		pidfile = config['pidfile']
	elif 'pidfile' in args:
		pidfile = args.pidfile
	else:
		sys.exit(1)

        try:
            # Obtain a lock
            statusLock(pidfile)
            # Grab the current status.
            currentStatus = requests.get(rssfeed).text
            # Generate alerts
            alerts = compareStatus(currentStatus,previousStatus,alertType,alertFilter,blacklist)
            # Release a lock
            statusUnlock(pidfile)
            sys.exit(0)
        except:
            # Clean up if lock exists.
            if os.path.isfile(pidfile):
                statusUnlock(pidfile)
            sys.exit(1)
