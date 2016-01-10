#!/usr/bin/env python3

import configparser
import os
import re
import socket
import sys
import urllib.parse
import urllib.request

from plumbum import local

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))

SMS_API_URL = 'https://api.smsapi.pl/sms.do'


def get_queue_size(mailq_output):
    num_regex = re.search(r'in (\d+) Request', mailq_output)
    if num_regex:
        return int(num_regex.group(1))
    elif re.match(r'Mail queue is empty', mailq_output):
        return 0
    else:
        raise Exception('invalid mailq input: ' + mailq_output)


def prepare_message(queue_size, mailq_output):
    subject = "[AUTO] Postfix shutdown on %s (%d messages)" % (socket.gethostname(), queue_size)

    message = "Postfix on '%s' was shut down because of perceived mail queue overflow. " % socket.gethostname()
    message += "The threshold was set to %d.\n\n" % CONFIG.getint('threshold', 'shutdown')
    message += "Mail queue dump:\n\n%s" % mailq_output

    return subject, message


def send_sms(message):
    post_data = {'message': message}
    for k, v in CONFIG.items('smsapi'):
        post_data[k] = v

    request = urllib.request.Request(SMS_API_URL, urllib.parse.urlencode(post_data).encode('utf-8'))
    response = urllib.request.urlopen(request)
    response.read()


if __name__ == "__main__":
    mailq_output = local['mailq']()
    queue_size = get_queue_size(mailq_output)

    if queue_size < CONFIG.getint('threshold', 'warning'):
        sys.exit(0)
    elif queue_size < CONFIG.getint('threshold', 'shutdown'):
        print("There are %d messages in Postfix queue." % queue_size)
        print("Mail queue dump:\n%s" % mailq_output)
        sys.exit(1)
    else:
        shutdown_postfix = local['service']['postfix']['stop']
        shutdown_postfix()

        subject, msg = prepare_message(queue_size, mailq_output)
        print(subject)
        print()
        print(msg)

        send_sms(subject)

        sys.exit(2)
