#!/bin/bash

if [[ "$#" -gt 0 ]]; then
    export MINUTE="*/$1"
else
    export MINUTE="*"
fi

(crontab -l ; echo "${MINUTE} * * * * `pwd`/virtualenv/bin/python `pwd`/manage.py do_alerting >/dev/null 2>&1") | sort | uniq - | crontab -