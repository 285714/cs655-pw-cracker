#!/bin/bash

cd /home/cs655-pw-cracker/

if [[ "$HOSTNAME" = server* ]]; then
    cd web
    sudo python3 httpserver.py
else
    cd src/worker
    python3 worker.py
fi

