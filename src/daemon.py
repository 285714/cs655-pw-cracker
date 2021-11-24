import time
from datetime import datetime


while True:
    with open("current_time", 'a') as f:
        now = datetime.now()
        print(now.strftime("%d.%m.%Y, %H:%M:%S"), file=f)
        time.sleep(1)


