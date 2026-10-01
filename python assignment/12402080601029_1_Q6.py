import heapq


n, e = map(int, input().split())

modules = []
graph = {}
indegree = {}

for _ in range(n):
    name = input().strip()
    modules.append(name)
    graph[name] = []
    indegree[name] = 0

for _ in range(e):
    a, b = input().split()

    if b not in graph[a]:
        graph[a].append(b)
        indegree[a] += 1

heap = []

for module in modules:
    if indegree[module] == 0:
        heapq.heappush(heap, module)

order = []

while heap:
    module = heapq.heappop(heap)
    order.append(module)

    for other in graph:
        if module in graph[other]:
            indegree[other] -= 1
            if indegree[other] == 0:
                heapq.heappush(heap, other)

if len(order) == n:
    print(*order)
else:
    state = {}
    path = []
    cycle = []

    def find_cycle(node):
        state[node] = 1
        path.append(node)

        for next_node in graph[node]:
            if state.get(next_node, 0) == 0:
                if find_cycle(next_node):
                    return True
            elif state.get(next_node) == 1:
                start = path.index(next_node)
                cycle.extend(path[start:])
                cycle.append(next_node)
                return True

        path.pop()
        state[node] = 2
        return False

    for module in modules:
        if state.get(module, 0) == 0 and find_cycle(module):
            break

    print("CYCLE", *cycle)
