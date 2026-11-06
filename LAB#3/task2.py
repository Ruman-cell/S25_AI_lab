graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [],
    "E": ["G"],
    "F": [],
    "G": ["H"],
    "H": []
}

def dls(start, goal, limit):
    stack = [(start, [start])]
    visited = []
    cutoff = False

    while stack:
        node, path = stack.pop()
        visited.append(node)

        if node == goal:
            return "FOUND", path, visited

        depth = len(path) - 1

        if depth == limit:
            if graph[node]:
                cutoff = True
        else:
            for child in reversed(graph[node]):
                if child not in path:
                    stack.append((child, path + [child]))

    if cutoff:
        return "CUTOFF", None, visited
    return "FAILURE", None, visited


for limit in [1, 2, 3,4]:
    status, path, visited = dls("A", "H", limit)

    print("Depth Limit:", limit)
    print("Status:", status)
    print("Path:", path)
    print("Visited Nodes:", visited)
    print('\n')
    print()
    if status == "FOUND":
        break