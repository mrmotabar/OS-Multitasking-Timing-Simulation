import time, hashlib
from random import randint

def random(l, r, mode = 1):
    rand = 0
    if mode == 0:
        now = time.time() + randint(0, 1000)
        hash_object = hashlib.sha256(str(now).encode())
        pbHash = hash_object.hexdigest()
        rand = int(pbHash, 16)
        rand %= (r - l)
        rand += l
    elif mode == 1:
        rand = randint(l, r - 1)
    return rand


def chisquare(randoms, l, r):
    e = len(randoms) * 1.0 / (r - l)
    chi2 = 0
    for i in randoms:
        chi2 += ((i - e) ** 2) / e
    return chi2


class Task:
    def __init__(self, Arrival_Time, Burst_Time):
        self.Arrival_Time = Arrival_Time
        self.Burst_Time = Burst_Time
        self.Remaining_Time = Burst_Time
        self.Wait_Time = 0
        self.State = "Ready"
        self.CPU = None

    def reset(self):
        self.Remaining_Time = self.Burst_Time
        self.Wait_Time = 0
        self.State = "Ready"
        self.CPU = None


class CPU:
    def __init__(self, Quantum = -1):
        self.Task = None
        self.Waiting_Time = 0
        self.Quantum = Quantum
        self.On_Task = 0

    def get_task(self, rq):
        if self.Task == None:
            task = rq.pop_front()
            self.Task = task
            if task != None:
                task.CPU = self
                task.State = "Running"

    def run(self):
        if self.Task != None:
            self.Task.Remaining_Time -= 1
            self.On_Task += 1
            if self.Task.Remaining_Time == 0:
                self.Task.State = "Terminated"
                self.Task = None
                self.On_Task = 0
            elif self.On_Task == self.Quantum:
                ret_task = self.Task
                self.Task.State = "Ready"
                self.Task = None
                self.On_Task = 0
                return ret_task
        else:
            self.Waiting_Time += 1


class Ready_Queue:
    def __init__(self):
        self.Queue = []

    def pop_front(self):
        if len(self.Queue) > 0:
            return self.Queue.pop(0)
        else:
            return None

    def push_back(self, task):
        self.Queue.append(task)

    def insert_in_order(self, task):
        if self.len() == 0 or task.Remaining_Time >= self.Queue[-1].Remaining_Time:
            self.push_back(task)
        elif task.Remaining_Time <= self.Queue[0].Remaining_Time:
            self.Queue.insert(0, task)
        else:
            s = 0
            e = self.len() - 1
            while e - s > 1:
                mid = (e + s) // 2
                if task.Remaining_Time < self.Queue[mid].Remaining_Time:
                    e = mid
                else:
                    s = mid
            self.Queue.insert(e, task)

    def len(self):
        return len(self.Queue)


class Dataset:
    def __init__(self, n, max_start, max_length):
        self.Data = []
        for i in range(n):
            self.Data.append(Task(random(0, max_start), random(1, max_length)))
        self.Data.sort(key = lambda task: task.Arrival_Time)

    def len(self):
        return len(self.Data)

    def reset(self):
        for i in range(len(self.Data)):
            self.Data[i].reset()


def FCFS(random_tasks, n_cpu):
    cpu = [CPU() for _ in range(n_cpu)]
    rq = Ready_Queue()
    ind = 0
    sum_waiting_tasks = 0
    sum_waiting_cpu = 0
    time = 0
    while True:
        if rq.len() == 0 and ind == random_tasks.len():
            break
        while ind < random_tasks.len() and random_tasks.Data[ind].Arrival_Time == time:
            rq.push_back(random_tasks.Data[ind])
            ind += 1
        for i in range(n_cpu):
            cpu[i].get_task(rq)
        for i in range(rq.len()):
            rq.Queue[i].Wait_Time += 1
        for i in range(n_cpu):
            cpu[i].run()
        time += 1
    for i in range(random_tasks.len()):
        sum_waiting_tasks += random_tasks.Data[i].Wait_Time
    for i in range(n_cpu):
        sum_waiting_cpu += cpu[i].Waiting_Time
    #print(sum_waiting_tasks / random_tasks.len())
    #print(sum_waiting_cpu / n_cpu)
    random_tasks.reset()
    return [sum_waiting_tasks / random_tasks.len(), sum_waiting_cpu / n_cpu]


def SJF(random_tasks, n_cpu):
    cpu = [CPU() for _ in range(n_cpu)]
    rq = Ready_Queue()
    ind = 0
    sum_waiting_tasks = 0
    sum_waiting_cpu = 0
    time = 0
    while True:
        if rq.len() == 0 and ind == random_tasks.len():
            break
        while ind < random_tasks.len() and random_tasks.Data[ind].Arrival_Time == time:
            rq.insert_in_order(random_tasks.Data[ind])
            ind += 1
        for i in range(n_cpu):
            cpu[i].get_task(rq)
        for i in range(rq.len()):
            rq.Queue[i].Wait_Time += 1
        for i in range(n_cpu):
            cpu[i].run()
        time += 1
    for i in range(random_tasks.len()):
        sum_waiting_tasks += random_tasks.Data[i].Wait_Time
    for i in range(n_cpu):
        sum_waiting_cpu += cpu[i].Waiting_Time
    #print(sum_waiting_tasks / random_tasks.len())
    #print(sum_waiting_cpu / n_cpu)
    random_tasks.reset()
    return [sum_waiting_tasks / random_tasks.len(), sum_waiting_cpu / n_cpu]
    

def RR_FCFS(random_tasks, Quantum, n_cpu):
    cpu = [CPU(Quantum) for _ in range(n_cpu)]
    rq = Ready_Queue()
    ind = 0
    sum_waiting_tasks = 0
    sum_waiting_cpu = 0
    time = 0
    while True:
        if rq.len() == 0 and ind == random_tasks.len():
            break
        while ind < random_tasks.len() and random_tasks.Data[ind].Arrival_Time == time:
            rq.push_back(random_tasks.Data[ind])
            ind += 1
        for i in range(n_cpu):
            cpu[i].get_task(rq)
        for i in range(rq.len()):
            rq.Queue[i].Wait_Time += 1
        for i in range(n_cpu):
            task = cpu[i].run()
            if task != None:
                rq.push_back(task)
        time += 1
    for i in range(random_tasks.len()):
        sum_waiting_tasks += random_tasks.Data[i].Wait_Time
    for i in range(n_cpu):
        sum_waiting_cpu += cpu[i].Waiting_Time
    #print(sum_waiting_tasks / random_tasks.len())
    #print(sum_waiting_cpu / n_cpu)
    random_tasks.reset()
    return [sum_waiting_tasks / random_tasks.len(), sum_waiting_cpu / n_cpu]
    

def RR_SJF(random_tasks, Quantum, n_cpu):
    cpu = [CPU(Quantum) for _ in range(n_cpu)]
    rq = Ready_Queue()
    ind = 0
    sum_waiting_tasks = 0
    sum_waiting_cpu = 0
    time = 0
    while True:
        if rq.len() == 0 and ind == random_tasks.len():
            break
        while ind < random_tasks.len() and random_tasks.Data[ind].Arrival_Time == time:
            rq.insert_in_order(random_tasks.Data[ind])
            ind += 1
        for i in range(n_cpu):
            cpu[i].get_task(rq)
        for i in range(rq.len()):
            rq.Queue[i].Wait_Time += 1
        for i in range(n_cpu):
            task = cpu[i].run()
            if task != None:
                rq.push_back(task)
        time += 1
    for i in range(random_tasks.len()):
        sum_waiting_tasks += random_tasks.Data[i].Wait_Time
    for i in range(n_cpu):
        sum_waiting_cpu += cpu[i].Waiting_Time
    #print(sum_waiting_tasks / random_tasks.len())
    #print(sum_waiting_cpu / n_cpu)
    random_tasks.reset()
    return [sum_waiting_tasks / random_tasks.len(), sum_waiting_cpu / n_cpu]
    

def std(l):
    mean = sum(l) / len(l)
    variance = sum([((x - mean) ** 2) for x in l]) / len(l)
    res = variance ** 0.5
    return res


f = open("Results.txt", "w")
sum_n_tasks = 0
sum_waiting_tasks_FCFS = [[], [], [], [], [], []]
sum_waiting_tasks_SJF = [[], [], [], [], [], []]
sum_waiting_tasks_RR_FCFS = [[], [], [], [], [], []]
sum_waiting_tasks_RR_SJF = [[], [], [], [], [], []]
sum_waiting_cores_FCFS = [[], [], [], [], [], []]
sum_waiting_cores_SJF = [[], [], [], [], [], []]
sum_waiting_cores_RR_FCFS = [[], [], [], [], [], []]
sum_waiting_cores_RR_SJF = [[], [], [], [], [], []]
for i in range(200):
    print(i)
    f.write(str(i + 1) + "\n")
    n_tasks = random(1000, 2000)
    sum_n_tasks += n_tasks
    max_start = random(10000, 40000)
    max_length = random(200, 500)
    f.write("number of tasks : " + str(n_tasks) + "\n")
    f.write("maximum start : " + str(max_start) + "\n")
    f.write("maximum length : " + str(max_length) + "\n")
    random_tasks = Dataset(n_tasks, max_start, max_length)
    for j in [1, 2, 5]:
        mean_waiting_tasks , mean_waiting_cpu = FCFS(random_tasks, j)
        f.write("mean tasks waiting time for FCFS with " + str(j) + " core : " + str(mean_waiting_tasks) + "\n")
        f.write("mean cores waiting time for FCFS with " + str(j) + " core : " + str(mean_waiting_cpu) + "\n")
        sum_waiting_tasks_FCFS[j].append(mean_waiting_tasks * n_tasks)
        sum_waiting_cores_FCFS[j].append(mean_waiting_cpu * j)
        mean_waiting_tasks , mean_waiting_cpu = SJF(random_tasks, j)
        f.write("mean tasks waiting time for SJF with " + str(j) + " core : " + str(mean_waiting_tasks) + "\n")
        f.write("mean cores waiting time for SJF with " + str(j) + " core : " + str(mean_waiting_cpu) + "\n")
        sum_waiting_tasks_SJF[j].append(mean_waiting_tasks * n_tasks)
        sum_waiting_cores_SJF[j].append(mean_waiting_cpu * j)
        mean_waiting_tasks , mean_waiting_cpu = RR_FCFS(random_tasks, 5, j)
        f.write("mean tasks waiting time for RR_FCFS with " + str(j) + " core : " + str(mean_waiting_tasks) + "\n")
        f.write("mean cores waiting time for RR_FCFS with " + str(j) + " core : " + str(mean_waiting_cpu) + "\n")
        sum_waiting_tasks_RR_FCFS[j].append(mean_waiting_tasks * n_tasks)
        sum_waiting_cores_RR_FCFS[j].append(mean_waiting_cpu * j)
        mean_waiting_tasks , mean_waiting_cpu = RR_SJF(random_tasks, 5, j)
        f.write("mean tasks waiting time for RR_SJF with " + str(j) + " core : " + str(mean_waiting_tasks) + "\n")
        f.write("mean cores waiting time for RR_SJF with " + str(j) + " core : " + str(mean_waiting_cpu) + "\n")
        sum_waiting_tasks_RR_SJF[j].append(mean_waiting_tasks * n_tasks)
        sum_waiting_cores_RR_SJF[j].append(mean_waiting_cpu * j)
    f.write("-------------------------------------------\n")
f.close()

f = open("Final_Result.txt", "w")
for i in [1, 2, 5]:
    f.write("mean tasks waiting time for FCFS with " + str(i) + " core : " + str(sum(sum_waiting_tasks_FCFS[i]) * 1.0 / sum_n_tasks) + "\n")
    f.write("sum cores waiting time for FCFS with " + str(i) + " core : " + str(sum(sum_waiting_cores_FCFS[i])) + "\n")
    f.write("std tasks waiting time for FCFS with " + str(i) + " core : " + str(std(sum_waiting_tasks_FCFS[i])) + "\n")
    f.write("std cores waiting time for FCFS with " + str(i) + " core : " + str(std(sum_waiting_cores_FCFS[i])) + "\n")
    f.write("\n")
    f.write("mean tasks waiting time for SJF with " + str(i) + " core : " + str(sum(sum_waiting_tasks_SJF[i]) * 1.0 / sum_n_tasks) + "\n")
    f.write("sum cores waiting time for SJF with " + str(i) + " core : " + str(sum(sum_waiting_cores_SJF[i])) + "\n")
    f.write("std tasks waiting time for SJF with " + str(i) + " core : " + str(std(sum_waiting_tasks_SJF[i])) + "\n")
    f.write("std cores waiting time for SJF with " + str(i) + " core : " + str(std(sum_waiting_cores_SJF[i])) + "\n")
    f.write("\n")
    f.write("mean tasks waiting time for RR_FCFS with " + str(i) + " core : " + str(sum(sum_waiting_tasks_RR_FCFS[i]) * 1.0 / sum_n_tasks) + "\n")
    f.write("sum cores waiting time for RR_FCFS with " + str(i) + " core : " + str(sum(sum_waiting_cores_RR_FCFS[i])) + "\n")
    f.write("std tasks waiting time for RR_FCFS " + str(i) + " core : " + str(std(sum_waiting_tasks_RR_FCFS[i])) + "\n")
    f.write("std cores waiting time for RR_FCFS " + str(i) + " core : " + str(std(sum_waiting_cores_RR_FCFS[i])) + "\n")
    f.write("\n")
    f.write("mean tasks waiting time for RR_SJF with " + str(i) + " core : " + str(sum(sum_waiting_tasks_RR_SJF[i]) * 1.0 / sum_n_tasks) + "\n")
    f.write("sum cores waiting time for RR_SJF with " + str(i) + " core : " + str(sum(sum_waiting_cores_RR_SJF[i])) + "\n")
    f.write("std tasks waiting time for RR_SJF " + str(i) + " core : " + str(std(sum_waiting_tasks_RR_SJF[i])) + "\n")
    f.write("std cores waiting time for RR_SJF " + str(i) + " core : " + str(std(sum_waiting_cores_RR_SJF[i])) + "\n")
    f.write("\n")
f.close()