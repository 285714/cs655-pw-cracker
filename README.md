# cs655-pw-cracker

Website: http://pcvm1-22.geni.it.cornell.edu:8080

Repo is cloned to /home/cs655-pw-cracker and start.sh is deamonized. Update by running `/install.sh`. To restart, run
```console
sudo systemctl restart cs655
```

## Instructions
On GENI, all scripts are automatically installed and the deamonized via systemctl. Note that the server node requires numpy, which can be installed as follows:
```console
sudo apt-get update
sudo apt install python3-pip
sudo pip3 install numpy
```

### To run locally:
To run workers: on several machines/ports run workers
```console
cd ./src/worker/  
python worker.py --port x, where x is the port number
```

To run the server:
* First, edit `./src/server/workers.py` to add the list of workers used. Each entry includes (hostname, port)

* Run the server:
```console
python server.py --hash h --num_workers n
```
Where h is a md5 hash and n is the number of workers to used.

### To run on GENI:
Create an instance, using rspec.xml GENI configuration file.
Wait for all components to start running. After that follow the instructions above.

### Set delays on nodes for the experiments
To change TCP Congestion Control version to Reno:
```console
sudo sysctl net.ipv4.tcp_congestion_control=reno
```

To setup a specific delay time  (to make sure that packets coming into the eth0 interface of any node will experience the delay):
```console
sudo tc qdisc add dev eth0 root netem delay [time]ms
```

To remove the setup:
```console
sudo tc qdisc del dev eth0 root netem
```
Note: we need to delete the old rules before setting up new ones.
The same setup/deletion command for eth1, eth2, etc. interfaces.
