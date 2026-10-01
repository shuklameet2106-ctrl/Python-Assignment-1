import heapq


w, n = map(int, input().split())

jobs = []

for i in range(n):
    arrival, job_id, priority, duration, resources = input().split()

    arrival = int(arrival)
    priority = int(priority)
    duration = int(duration)
    resources = int(resources)

    jobs.append((arrival, i, job_id, priority, duration, resources))

jobs.sort()

workers = [(0, i + 1) for i in range(w)]
heapq.heapify(workers)

waiting = []
time = 0
index = 0
results = []
total_wait = 0

while index < n or waiting:
    if not waiting and index < n:
        time = max(time, jobs[index][0])

    while index < n and jobs[index][0] <= time:
        arrival, order, job_id, priority, duration, resources = jobs[index]
        heapq.heappush(waiting, (-priority, arrival, order, job_id, duration, resources))
        index += 1

    worker_free, worker_id = heapq.heappop(workers)

    if worker_free > time:
        time = worker_free

    while index < n and jobs[index][0] <= time:
        arrival, order, job_id, priority, duration, resources = jobs[index]
        heapq.heappush(waiting, (-priority, arrival, order, job_id, duration, resources))
        index += 1

    if waiting:
        priority, arrival, order, job_id, duration, resources = heapq.heappop(waiting)
        start = max(time, arrival)
        finish = start + duration

        total_wait += start - arrival

        results.append((start, job_id, worker_id, finish))
        heapq.heappush(workers, (finish, worker_id))
        time = start
    else:
        heapq.heappush(workers, (worker_free, worker_id))

results.sort()

for start, job_id, worker_id, finish in results:
    print(job_id, f"W{worker_id}", start, finish)

print(f"AVG_WAIT {total_wait / n:.2f}")
