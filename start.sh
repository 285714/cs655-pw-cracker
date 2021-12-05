#!/bin/bash

cd /home/cs655-pw-cracker/

if [[ "$HOSTNAME" = server* ]]; then
    cd web
    sudo python3 httpserver.py > log
else
    cd src/worker
    python3 worker.py > log
fi

