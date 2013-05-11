#!/bin/bash

(crontab -l ; echo "* * * * * `pwd`/virtualenv/bin/python `pwd`/manage.py do_monitoring >/dev/null 2>&1") | sort | uniq - | crontab -