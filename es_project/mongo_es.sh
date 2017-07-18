#!/bin/bash

NAME="elasticsearch"                                 #Name of the application
DJANGODIR=/home/ubuntu/es_project/es_project         #Django project directory
USER=ubuntu                                          #the user to run as
NUM_WORKERS=3                                        #how many worker processes should Gunicorn spawn

# Which settings file should Django use
DJANGO_SETTINGS_MODULE=es_project.settings
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

# Django project directory
DJANGO_WSGI_MODULE=es_project.wsgi

# Host has to be same as NGINX.conf
HOST=127.0.0.1
PORT=8001

echo "Starting $APP_NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source ../bin/activate
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ../bin/gunicorn $DJANGO_WSGI_MODULE:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER \
  --bind=$HOST:$PORT \
  --log-level=debug \
  --log-file=-
