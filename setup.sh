#! /bin/sh
cd /opt/app-root/src
echo 'starting upgrade'
/opt/app-root/bin/python manage.py db upgrade
