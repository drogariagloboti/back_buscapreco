import queue
from control import exec_minibanner


mini_banners = queue.Queue()


def next():
    if mini_banners.qsize() <= 2:
        ret = exec_minibanner()
        for i in ret:
            mini_banners.put(item=i)
    print(mini_banners.qsize())
    return mini_banners.get()
