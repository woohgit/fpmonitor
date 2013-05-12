#!/bin/bash

if [[ "$#" -gt 0 ]]; then
    if [[ "$1" == "--start" ]]; then
        (crontab -l ; echo "* * * * * cd `pwd` && `pwd`/virtualenv/bin/python `pwd`/manage.py do_alerting >/dev/null 2>&1") | sort | uniq - | crontab -
    else
        (crontab -l | grep -v 'do_alerting') | sort | uniq - | crontab -
    fi
else
    echo "Usage: ./cron_alerting.sh [--start, --stop]"
fi

