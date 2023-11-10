import queue
from control import exec_minibanner


mini_banners = queue.Queue()


def next():
    if mini_banners.qsize() == 0:
        ret = exec_minibanner()
        for i in ret:
            mini_banners.put(item=i)
    print(mini_banners.qsize())
    nnext = mini_banners.get()
    mini_banners.task_done()
    return nnext
