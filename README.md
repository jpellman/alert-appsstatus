# Google Apps Status Notification Script

With the large number of Google Apps outages throughout June 2019, I found it prudent (as a G Suite admin) to look for a means to be alerted of G Suite service degradations via e-mail, text or both.  Perhaps this was me just being an idiot, but I couldn't find any official means for receiving such alerts.

This script is an attempt at remedying this oversight.  It is intended to be run as a cron job at a periodic interval.  Right now, it's in its early iterations / is a minimal viable product.  

## How it works

The script uses the feedparser library to convert the Apps Status [RSS feed](https://www.google.com/appsstatus/rss/en) into an object that can be checked against various alert criteria.  If one of the alert criteria is fulfilled, it sends an e-mail or a text (by sending an e-mail to an "@vtext.com" or "@txt.att.net").  Currently texts must be encoded as e-mail addresses, although I'd like to add some logic to allow numbers to be accepted directly (possibly via twilio).

The alert criteria are defined in a YAML file.  Alerting can be continous or only upon state changes.  To track state changes, the script caches the previous results of the RSS feed locally for comparison before the next time the script is run.

The script uses a lock file (_~appsstatus.lock_) to prevent race conditions.

## To-Do

 * Actually use YAML files for configuration.
 * Implement a whitelist in case we only care about certain G Suite services.
 * Attempt to add compatibility with Python 2 / make this work across all Pythons.
 * Add logging
 * Add better support for text messaging other than "use @vtext.com addresses".
 * At some point I'd like to convert this into a proper PyPI package.

## Other Projects of Interest for G Suite Admins

 * [google-status-notifications](https://github.com/bitle/google-status-notifications) : Attempts to do the same thing as this script.  Doesn't seem to have any documentation, looks unmaintained, and lots of unnecessary dependencies.  The repo has an example of an RSS feed during a G Suite outage though, which I've been using for testing.
 * [g_suite_status](https://twitter.com/g_suite_status) : Someone made a Twitter bot to monitor G Suite outages.
 * [icssplit](https://github.com/beorn/icssplit) : For some reason Google Calendar only supports calendar imports for files that are less than 1 MB.  This allows you to work around that.
