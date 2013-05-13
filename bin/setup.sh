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

# pip should fail, so to be sure we can install all deps
while true;
do
  pip install --exists-action w -r requirements.txt
  if [ "$?" -eq 0 ]; then
    break;
  fi
done

if ./manage.py validate ; then
    echo "django settings OK"
else
    echo "ERROR in Django"
    exit -1
fi

case $1 in
    --server)
    ./manage.py syncdb --noinput
    ./manage.py loaddata sample_data.json
    ;;
esac

echo "Installation complete!"
