#!/bin/bash
export C_FORCE_ROOT="true"
git --git-dir=$PWD/pyTasks/.git  --work-tree=$PWD/pytasks/ pull 
celery -A tasks worker -b $MASTER_IP --workdir=$PWD/pyTasks &
