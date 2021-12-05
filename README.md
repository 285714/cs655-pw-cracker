# cs655-pw-cracker

Website: http://pcvm1-22.geni.it.cornell.edu/

Repo is cloned to /home/cs655-pw-cracker and start.sh is always running. Update by running install.sh.

## Update 02/12

To test/run:

On several machines/ports run workers

cd ./src/worker/  
python worker.py --port x, where x is the port number

To test the server
* first, edit ./src/server/workers.py to add the list of workers used. Each entry includes (hostname, port)
* Run the server: python server.py --hash h --num_workers n, where h is a md5 hash and n is the number of workers to used.

As of 02/12, the server can handle one request and multiple workers. One can test what happens if a worker dies by stopping the worker code. We need to devise a way to test the worker delay. 

TODO:   
- [ ] handle the case when all worker dies, the server needs to terminate the processes.  
- [ ] connect the web and the server, handle multiple requests from the web
- [ ] port to geni and test
