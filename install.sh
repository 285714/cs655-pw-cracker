git clone git@github.com:285714/cs655-pw-cracker.git
cd cs655-pw-cracker

sudo mv cs655.service /etc/systemd/system
sudo systemctl start cs655.service
sudo systemctl enable cs655.service

