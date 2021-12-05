# list of workers, each specified by a hostname + port
import os
import re
import socket


if socket.gethostname().startswith("server"):
    interfaces = os.popen("ifconfig").read().split("\n\n")
    WORKERS = []
    for interface in interfaces:
        m = re.search("(eth[1-9]\d*):", interface)
        if m is None: continue
        name = m[1]
        m = re.search("inet (\S+)", interface)
        ip = m[1]
        WORKERS.append((ip, 58800))

else:
    WORKERS = [
        ("localhost", 58800),
        ("localhost", 58801)
    ]


