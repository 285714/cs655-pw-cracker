# list of workers, each specified by a hostname + port
import os
import re
import socket


public_ip_workers = [
        ("165.124.51.201", 58800),
        ("165.124.51.197", 58800),
        ("165.124.51.202", 58800),
    ]


if socket.gethostname().startswith("server"):
    interfaces = os.popen("ifconfig").read().split("\n\n")
    WORKERS = []
    for interface in interfaces:
        m = re.search("(eth[1-9]\d*):", interface)
        if m is None: continue
        name = m[1]
        m = re.search("inet (\S+)\.(\d+)", interface)
        ip_l = m[1]
        ip_r = int(m[2])
        ip = ip_l + "." + str(3 - ip_r)
        WORKERS.append((ip, 58800))

    WORKERS = WORKERS + public_ip_workers

else:
    WORKERS = [
        ("localhost", 58800),
        ("localhost", 58801)
    ]


