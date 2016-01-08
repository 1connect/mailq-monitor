import re
import socket
import sys

from plumbum import local

WARNING_THRESHOLD = 5
SHUTDOWN_THRESHOLD = 20


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
    message += "The threshold was set to %d.\n\n" % SHUTDOWN_THRESHOLD
    message += "Mail queue dump:\n\n%s" % mailq_output

    return subject, message


def send_sms(message):
    # todo send sms message
    pass


if __name__ == "__main__":
    mailq_output = local['mailq']()
    queue_size = get_queue_size(mailq_output)

    if queue_size < WARNING_THRESHOLD:
        sys.exit(0)
    elif queue_size < SHUTDOWN_THRESHOLD:
        print("There are %d messages in Postfix queue." % queue_size)
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
