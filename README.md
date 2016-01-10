# Postfix queue monitor

If you host several Wordpress websites, there's a great deal of possibility
that one of them might be compromised and become a SPAM sender. SPAM is usually
rejected by the recipients so queue gets longer and longer. The script
checks the length of Postfix queue and performs appropriate actions depending
on the queue length.

It'll help you protecting your server from becoming SPAM sender
and getting blacklisted in consequence.

There are two levels defined:
* **warning** - if mail queue is longer than warning value, the script prints
warning to *stdout* since the script should be called from *cron*, the output
is sent to *root*

* **shutdown** - if queue is longer than specified `shutdown` parameter,
Postfix is shut downand SMS message is sent

## Installation

* Install required packages:
```bash
apt-get install python3-plumbum
```

* Clone repository and edit config file:
```bash
git clone https://github.com/1connect/mailq-monitor.git
cd mailq-monitor
cp example.config.ini config.ini
```

* Add the following line to *crontab* (using `crontab -e`):
```
* * * * * /root/mailq-monitor/mailq_check.py
```
