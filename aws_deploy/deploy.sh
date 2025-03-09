#!/bin/bash
cd /home/ubuntu/fitbit_project
git pull origin main
pkill gunicorn
nohup gunicorn --bind 0.0.0.0:5000 app:app > app.log 2>&1 &