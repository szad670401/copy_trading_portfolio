from multiprocessing import Process, Queue
from multiprocessing.dummy import Pool as ThreadPool
import requests
import time
import config


class DingTalkServer:
    def __init__(self, api_url: str = None, max_qua_per_src: int = 10):
        self.api_url = "https://oapi.dingtalk.com/robot/send?access_token=" + \
            config.dingtalk_token
        self.msg_queue = Queue(1)
        self.msg_interval = 1 / max_qua_per_src

    def send_message(self, content):
        content = {
            "msgtype": "text",
            "text": {
                "content": '内容：' + content}
        }
        headers = {"Content-Type": "application/json;charset=utf-8"}
        url = self.api_url
        r = requests.post(url=url, headers=headers, json=content)
        return r.content

    def log_msg(self, msg):
        if not self.msg_queue.full():
            self.msg_queue.put(msg)
            return True
        else:
            return False

    def run_server(self):
        def msg_queue_thread():
            while True:
                content,interval   = self.msg_queue.get()
                if isinstance(content, str):
                    self.send_message(content)
                    time.sleep(self.msg_interval)
                    time.sleep(interval)
        thread = Process(target=msg_queue_thread)
        thread.start()


def dprint(*args,interval = 1):
    info = ""
    for arg in args:
        info += str(arg) + " "
    return ding_talk_server.log_msg([info , interval])


ding_talk_server = DingTalkServer()
ding_talk_server.run_server()


