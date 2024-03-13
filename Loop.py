from multiprocessing import Process
from time import sleep
import requests

class Loop:
    def __init__(self, start=0, end=0, access_token="") -> None:
        self.start = start
        self.end = end
        self.duration = (end - start)/1000
        self.access_token = access_token
        self.loop = None

    def start_loop(self):
        self.loop = Process(target=self.request_loop)
        self.loop.start()

    def stop_loop(self):
        self.loop.terminate()
        self.loop = None

    def set_start(self, start):
        self.start = start
        self.duration = (self.end - self.start)/1000

    def set_end(self, end):
        self.end = end
        self.duration = (self.end - self.start)/1000

    def request_loop(self):
        request_url = "https://api.spotify.com/v1/me/player/seek?position_ms=" + str(self.start)
        headers = {
            'Authorization':'Bearer ' + self.access_token
        }
        while(True):
            requests.put(request_url, headers=headers)
            sleep(self.duration)