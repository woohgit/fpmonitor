#!/bin/bash

if [[ "$#" -eq 1 ]]; then
    if [[ "$1" == "--stop" ]]; then
        (crontab -l | grep -v 'do_monitoring') | sort | uniq - | crontab -
    else
        echo "Usage: ./cron_monitoring [--start n|--stop]"
    fi
else
    if [[ "$2" -eq 1 ]]; then
        export MINUTE="*"
    else
        export MINUTE="*/$2"
    fi
    (crontab -l ; echo "${MINUTE} * * * * `pwd`/virtualenv/bin/python `pwd`/manage.py do_monitoring >/dev/null 2>&1") | sort | uniq - | crontab -
fi

