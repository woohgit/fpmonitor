#!/bin/bash

if [[ ! -e manage.py ]] ; then
 echo "Run from the root directory!"
 exit -1
fi

if [[ "$1" == "--force" ]] ; then
    rm -rf virtualenv
    rm fpmonitor.db
fi

if [[ ! -e virtualenv ]] ; then
    virtualenv -p python2.6 virtualenv
fi

source virtualenv/bin/activate

pip install -r requirements.txt

if ./manage.py validate ; then
    echo "django settings OK"
else
    echo "ERROR in Django"
    exit -1
fi

./manage.py syncdb --noinput
./manage.py loaddata sample_data.json
