from datetime import datetime
from time import sleep

while(True):
    now = int(datetime.now().timestamp() * 1000)
    arle = int(datetime(2024, 3, 11, 6, 0, 0, 0).timestamp() * 1000)
    print(arle - now)