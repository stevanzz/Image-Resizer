# Imageresizer
The django image resizer app

# Getting started
1. Make one folder, for example, $ mkdir webapps
2. Clone this project, by typing $ git clone https://github.com/Shoppr/imageresizer
3. Set virtualenv for the project (in the current folder, just to make it looks neater), by typing $ virtualenv .
4. Move inside the project, $ cd imageresizer
5. Install all the requirements from requirements.txt, by using $ pip install -r requirements.txt
6. Move outside the project (back to webapps folder), $ cd ..
7. Activate the project, by using $ source bin/activate
8. Move the mymiddleware.py to /webapps/lib/site-packages/django/middleware (for turning off auto-append slash in urls only)
9. Override the MIDDLEWARE in settings.py by typing "django.middleware.mymiddleware.RedirectToNoSlash" at the first part in the list

## Nginx
NGINX (pronounced "engine x") is a web server. It can act as a reverse proxy server for HTTP, HTTPS, SMTP, POP3, and IMAPprotocols, as well as a load 
balancer and an HTTP cache.  This architecture uses small, but more importantly, predictable amounts of memory under load. Even if you don’t expect to handle 
thousands of simultaneous requests, you can still benefit from NGINX’s high-performance and small memory footprint. 

NGINX scales in all directions: from the smallest VPS all the way up to large clusters of servers.

### Installing NGINX: 
(Ubuntu) $ sudo apt-get install nginx

### Editing NGINX.conf: 
1. Folder location, $ cd /etc/nginx/sites-enabled  
2. Create new conf file by typing $ sudo nano conf_file_name.conf  

Example of .conf file:  
```
Server {  
	server_name 0.0.0.0;			#listen to all ip address
	client_max_body_size 30M;
	access_log <project_path>/logs/nginx-access.log

	location /static/ {			#location of static files
		alias /home/ubuntu/webapps/imageresizer/testing/static/images/;
		sendfile on;
		tcp_nopush on;
		tcp_nodelay on;
	}
	location /media/ {			#location of media files
		alias /home/ubuntu/webapps/imageresizer/testing/media/images/;
	}

	#This is for handling favicon.ico request error
	location = /favicon.ico {
             	return 204;
               	access_log off;
               	log_not_found off;
	}

	#Finally, send all non-media requests to the Django server.
	location / {
		proxy_pass http://127.0.0.1:8001;	#must be the same as Gunicorn ip address
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	} 
}
```

3. Ctrl + O to write out (save), Ctrl + X to exit  
4. After creating it, restart the NGINX service by, $ sudo service nginx restart  

## Gunicorn
Gunicorn ‘Green Unicorn’ is a Python WSGI HTTP Server for UNIX. It’s a pre-fork worker model ported from Ruby’s Unicorn project. 
The Gunicorn server is broadly compatible with various web frameworks, simply implemented, light on server resources, and fairly speedy.

### Installing Gunicorn:
1. Make sure you are in activate mode of your project, $ source bin/activate or $ workon  
2. $ pip install gunicorn  

### Running Gunicorn:
1. Go to the root of your project (where manage.py located)  
2. Type $ gunicorn imageresizer.wsgi:application -bind 127.0.0.1:8001 	#the ip address has to be same as NGINX.conf  
Note: if the port is already in used, kill the port by $ sudo kill $(sudo lsof -t -i:8001), then start the gunicorn  


## Combining NGINX + Gunicorn + Django:
Makes a .sh(shell) file in the root of the project (where manage.py located)

Example of .sh file:  
```
NAME="imageresizer"                             	#Name of the application
DJANGODIR=/home/ubuntu/webapps/imageresizer     	#Django project directory
USER=ubuntu                                      	#the user to run as
GROUP=webapps                                   	#the group to run as
NUM_WORKERS=3                                   	#how many worker processes should Gunicorn spawn

# Which settings file should Django use
DJANGO_SETTINGS_MODULE=imageresizer.settings
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

# Django project directory
DJANGO_WSGI_MODULE=imageresizer.wsgi

# Host has to be same as NGINX.conf
HOST=127.0.0.1
PORT=8001

echo "Starting $APP_NAME as `whoami`"

# Activate the virtual environment
cd $DJANGO_DIR
source ../bin/activate
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ../bin/gunicorn $DJANGO_WSGI_MODULE:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=$HOST:$PORT \
  --log-level=debug \
  --log-file=-
```

Well done! your gunicorn should have worked right now!  
To try it:  
1. Start running your gunicorn  
2. Try visit the ip address of your machine from other machine  
3. Try visit the url address of your django project from other machine 

# Supervisor
We need to make sure that the Gunicorn starts automatically with the system and that it can automatically restart if for some reason it exits unexpectedly. 

## Installing Supervisor 
1. Go to /etc/supervisor/conf.d, $ cd /etc/supervisor/conf.d  
2. Make a .conf file, $ vi imageresizer.conf  

Example of .conf file:  
```
[program:imageresizer]
command = /home/ubuntu/webapps/imageresizer/imageresizer.sh           ; Command to start app
directory=/home/ubuntu/webapps/imageresizer
stdout_logfile = /home/ubuntu/webapps/imageresizer/logs/debug.log     ; Where to write log messages
redirect_stderr = true                                                ; Save stderr in the same log
environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8                       ; Set UTF-8 as default encoding
```
3. Save the file, press "Esc" and type ":wq" (write and quit)
4. Don't forget to make logs folder for supervisor in the path you have specified  
5. Type $ sudo supervisorctl reread  
6. Type $ sudo supervisorctl update  

## Command in Supervisor
Example of command in Supervisor:
```
$ sudo supervisorctl status imageresizer                       
imageresizer                            RUNNING    pid 18020, uptime 0:00:50
$ sudo supervisorctl stop imageresizer
imageresizer: stopped
$ sudo supervisorctl start imageresizer
imageresizer: started
$ sudo supervisorctl restart imageresizer
imageresizer: stopped
imageresizer: started
```
