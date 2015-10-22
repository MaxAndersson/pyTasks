#!/bin/bash
sudo apt-get update -y
sudo apt-get install git -y
sudo apt-get install python-pip -y
sudo pip install Flask
sudo apt-get install rabbitmq-server -y
sudo rabbitmq-plugins enable rabbitmq_management
sudo pip install celery
sudo pip install flower
git clone https://github.com/MaxAndersson/pyTasks.git
sudo flower -A tasks --port=5555 --workdir=$PWD/pyTasks &
python pyTasks/app.py
