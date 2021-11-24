#!/bin/bash

sudo chmod -R a+rwX /home
cd /home

if cd cs655-pw-cracker
then
  git pull
else
  git clone https://github.com/285714/cs655-pw-cracker.git
  cd cs655-pw-cracker
fi

sudo cp cs655.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable cs655.service
sudo systemctl restart cs655.service
