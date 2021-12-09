# cs655-pw-cracker

Website: http://pcvm1-22.geni.it.cornell.edu:8080

Repo is cloned to /home/cs655-pw-cracker and start.sh is always running. Update by running install.sh. Restart with 'sudo systemctl restart cs655'

## Update 02/12

To test/run:

On several machines/ports run workers

```console
cd ./src/worker/  
python worker.py --port x, where x is the port number
```

To test the server:
* First, edit ./src/server/workers.py to add the list of workers used. Each entry includes (hostname, port)
* Run the server:
```console
python server.py --hash h --num_workers n
```
Where h is a md5 hash and n is the number of workers to used.

[NEED DELETE OR EDIT THIS] The server can handle one request and multiple workers. One can test what happens if a worker dies by stopping the worker code. We need to devise a way to test the worker delay.

TODO:   
- [x] handle the case when all worker dies, the server needs to terminate the processes (after some reconnection attempts).  
- [x] connect the web and the server, handle multiple requests from the web
- [x] port to geni and test
- [x] add more workers (double check whether IP addresses are guessed correctly by server/workers.py)
- [ ] run experiments and add plots to the report

## Required Packages (on server)
```console
sudo apt-get update
sudo apt install python3-pip
sudo pip3 install numpy
```

## Set Delays on nodes
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
