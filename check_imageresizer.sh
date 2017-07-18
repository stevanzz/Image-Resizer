#!/bin/bash

while true; do
	status_code=`curl -so /dev/null -w '%{response_code}' http://img.shopprapp.io/q/https://lh3.googleusercontent.com/-5pCFUQtEElY/UyKhFaX6DqI/AAAAAAAAOPw/LtALlKck5H8SPqzderTh0S6U0lm8N4RqACHM/s251/chrome-a_512.png`
	if [ "$status_code" == 200 ]; then
		date +"%T"
		echo "imageresizer success"
	else
		date +"%T"
	        echo "imageresizer fail"
		sudo supervisorctl restart imageresizer
	fi
	echo "---------------------------------------"
	sleep 600
done;
