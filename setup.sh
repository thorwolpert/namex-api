#! /bin/sh
export LIBRARY_PATH=/opt/rh/httpd24/root/usr/lib64
export X_SCLS=rh-python35 rh-nodejs6 httpd24
export LD_LIBRARY_PATH=/opt/rh/rh-python35/root/usr/lib64:/opt/rh/rh-nodejs6/root/usr/lib64:/opt/rh/httpd24/root/usr/lib64
export PATH=/opt/app-root/bin:/opt/rh/rh-python35/root/usr/bin:/opt/rh/rh-nodejs6/root/usr/bin:/opt/rh/httpd24/root/usr/bin:/opt/rh/httpd24/root/usr/sbin:/opt/app-root/src/.local/bin/:/opt/app-root/src/bin:/opt/app-root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH=/opt/rh/rh-nodejs6/root/usr/lib/python2.7/site-packages


cd /opt/app-root/src
echo 'starting upgrade'
/opt/app-root/bin/python manage.py db upgrade
