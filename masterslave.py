from multiprocessing import Process, Semaphore, Queue


class Master(object):
    def __init__(self, epoch, client_num, gather_lock, gather_queue, sendback_queue):
        self.epoch = epoch
        self.client_num = client_num
        self.gather_lock = gather_lock
        self.gather_queue = gather_queue
        self.sendback_queue = sendback_queue
        self.p = Process(target=self.send_recv)

    def start(self):
        self.p.start()


    def send_to_client(self, data):
         # ----  send back:
        for _ in range(self.client_num):
            self.sendback_queue.put(data)
        print('send back')

    def distribute(self):
        data = [12,2]
        self.send_to_client(data)

    def recv_send(self):
        i=0
        while i < self.epoch:
            i+=1
            print('epoch:', i)

            if i == 1:
                self.distribute()
                continue

            # ----  receive data
            data = []
            while True:
                d = self.gather_queue.get(block=True)
                if d == self.client_num:
                    break

            # ----   receive end
            data_to_send = self.compute()

            # ----  send back:
            self.send_to_client(data_to_send)
            print('send back')

            
    def compute(self):
        print('master compute')


class Slave(object):
    def __init__(self, epoch, gather_lock ,gather_queue, sendback_queue):
        self.epoch = epoch
        self.gather_lock = gather_lock
        self.gather_queue = gather_queue
        self.sendback_queue = sendback_queue
        self.p = Process(target=self.send_recv)

    def compute(self):
        print('do task')
        return "data"

    def compute_from_master(self, data_from_master):
        print('compute from master')

    def recv_from_master(self):
        return self.sendback_queue.get(block=True)

    def send_to_master(self, data):
        print("sending to gather queue")
        return self.gather_queue.put(data)

    def send_recv(self):
        i=0
        while i < self.epoch:
            i+=1
            print('epoch:', i)

            if i == 1:
                data= self.recv_from_master()

            # before send functions
            data = self.compute()
            # ----end ----
            # send to master
            ok = self.send_to_master(data)
            # ------ send end

            # recv from master from i = 2 :
            recv_data = self.recv_from_master() 
            print('recv from master:', recv_data)
            # after send  implemente your functions
            self.compute_from_master(recv_data)

    def start(self):
        self.p.start()


if __name__ == "__main__":

    client_num = 10

    gather_lock=Semaphore(client_num)
    gather_queue = Queue(client_num)

    sendback_queue = Queue(client_num)

    master = Master(client_num, gather_lock ,gather_queue, sendback_queue)
    master.start()

    for i in range(client_num):
        slave = Slave(client_num, gather_lock ,gather_queue, sendback_queue)
        slave.start()






