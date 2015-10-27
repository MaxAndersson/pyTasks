#!/bin/bash
git --git-dir=$PWD/pyTasks/.git  --work-tree=$PWD/pytasks/ pull
sudo flower -A tasks --port=5555 --workdir=$PWD/pyTasks &
python pyTasks/app.py
