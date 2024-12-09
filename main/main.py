from multiprocessing import Process, Queue
from stream_kline_binance import websocket_kline
from market_kline_binance import market_kline
from stream_depth_binance import websocket_depth

def processlogic(queue, queue_depth):
    while True:
        
        kline = queue.get()
        depth = queue_depth.get()
        # print(f'kline: {kline}')
        # print(f'depth: {depth}')


if __name__ == "__main__":
    market_kline()
    queue = Queue()
    queue_depth = Queue()

    WebKline = Process(target=websocket_kline, args=(queue,))
    WebKline.start()
    WebDepth = Process(target=websocket_depth, args=(queue_depth,))
    WebDepth.start()

    try:
        processlogic(queue, queue_depth)
    except:
        WebKline.terminate()
        WebKline.join()