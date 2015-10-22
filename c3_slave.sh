#!/bin/bash
export C_FORCE_ROOT="true"
sudo apt-get update -y
sudo apt-get install git -y
sudo apt-get install python-pip -y
sudo pip install celery
sudo pip install python-swiftclient
sudo pip install python-keystoneclient
sudo pip install python-novaclient
git clone https://github.com/MaxAndersson/pyTasks.git
celery -A tasks worker -b $MASTER_IP --workdir=$PWD/pyTasks &
