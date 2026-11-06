from __future__ import annotations

import heapq
from dataclasses import dataclass
from math import inf

Graph = dict[str, list[tuple[str, int]]]
GRAPH: Graph = {
    "S": [("A", 1), ("B", 4)],
    "A": [("C", 2)],
    "B": [("G", 5)],
    "C": [("G", 3)],
    "G": [],
}
HEURISTIC = {"S": 5, "A": 4, "B": 4, "C": 2, "G": 0}
START, GOAL = "S", "G"


@dataclass
class SearchResult:
    path: list[str]
    reported_cost: int
    processed: list[str]
    expanded: list[str]
    trace: list[dict]
    stale_ignored: int
    pending_frontier_at_goal: list[tuple[int, int, str]]

    @property
    def expansion_count(self) -> int:
        return len(self.expanded)


def route_cost(graph: Graph, path: list[str]) -> int:
    """Independently sum actual edge weights for the returned path."""
    total = 0
    for source, dest in zip(path, path[1:]):
        matched = [cost for neighbor, cost in graph[source] if neighbor == dest]
        if not matched:
            raise ValueError(f"Invalid route edge: {source} -> {dest}")
        total += matched[0]
    return total


def frontier_snapshot(pq: list[tuple[int, int, str, list[str]]], best: dict[str, int], h: dict[str, int]) -> list[dict]:
    """Sorted active queue entries, with stale records excluded from the display."""
    active = sorted((f, g, node, path) for f, g, node, path in pq if g == best.get(node))
    return [{"node": node, "g": g, "h": h[node], "f": f, "path": path} for f, g, node, path in active]


def search(graph: Graph, h: dict[str, int], start: str, goal: str) -> SearchResult:
    """A* search; providing h=0 for all nodes makes this an identical UCS control."""
    if any(weight < 0 for outgoing in graph.values() for _, weight in outgoing):
        raise ValueError("UCS/A* here requires nonnegative edge weights")
    if start not in graph or goal not in graph:
        raise ValueError("Start and goal must be present")
    if any(node not in h for node in graph):
        raise ValueError("Every graph node needs a heuristic value")
    pq: list[tuple[int, int, str, list[str]]] = [(h[start], 0, start, [start])]
    best = {start: 0}
    processed: list[str] = []
    expanded: list[str] = []
    trace: list[dict] = []
    stale_ignored = 0

    while pq:
        # Tie-breaking: first f, then g, then node label (and path if still tied).
        f, g, node, path = heapq.heappop(pq)
        if g != best[node]:
            stale_ignored += 1
            trace.append({"event": "stale", "node": node, "g": g, "f": f})
            continue
        processed.append(node)
        if node == goal:
            trace.append({"event": "goal", "node": node, "g": g, "h": h[node], "f": f,
                          "frontier": frontier_snapshot(pq, best, h)})
            return SearchResult(path, g, processed, expanded, trace, stale_ignored,
                                [(entry[0], entry[1], entry[2]) for entry in pq])

        expanded.append(node)
        for nxt, weight in graph.get(node, []):
            ng = g + weight
            if ng < best.get(nxt, inf):
                best[nxt] = ng
                heapq.heappush(pq, (ng + h[nxt], ng, nxt, path + [nxt]))
        trace.append({"event": "expand", "node": node, "g": g, "h": h[node], "f": f,
                      "frontier": frontier_snapshot(pq, best, h)})

    raise ValueError(f"Goal {goal} is unreachable from {start}")


def shortest_remaining_costs(graph: Graph, goal: str) -> dict[str, int]:
    """Independent exact costs to goal using reverse-edge Dijkstra."""
    reverse: dict[str, list[tuple[str, int]]] = {node: [] for node in graph}
    for src, outgoing in graph.items():
        for dst, weight in outgoing:
            reverse[dst].append((src, weight))
    dist = {node: inf for node in graph}
    dist[goal] = 0
    pq: list[tuple[int, str]] = [(0, goal)]
    while pq:
        d, node = heapq.heappop(pq)
        if d != dist[node]:
            continue
        for prev, w in reverse[node]:
            if d + w < dist[prev]:
                dist[prev] = d + w
                heapq.heappush(pq, (d + w, prev))
    return dist


def fmt_frontier(frontier: list[dict]) -> str:
    return ", ".join(f"{e['node']}(g={e['g']},h={e['h']},f={e['f']})" for e in frontier) or "(empty)"


def display_run(label: str, h: dict[str, int]) -> SearchResult:
    result = search(GRAPH, h, START, GOAL)
    print(f"\n=== {label} ===")
    for i, step in enumerate(result.trace, start=1):
        if step['event'] == 'expand':
            print(f"EXPAND {step['node']}: g={step['g']}, h={step['h']}, f={step['f']}; frontier: {fmt_frontier(step['frontier'])}")
        elif step['event'] == 'goal':
            print(f"PROCESS GOAL {step['node']}: g={step['g']} (not an expansion)")
        else:
            print(f"SKIP STALE {step['node']}: g={step['g']}")
    print(f"Processed nodes: {' -> '.join(result.processed)}")
    print(f"Expanded nodes:  {' -> '.join(result.expanded)}")
    print(f"Expansion count: {result.expansion_count} (goal excluded)")
    print(f"Returned path:   {' -> '.join(result.path)}")
    print(f"Reported path cost: {result.reported_cost}")
    print(f"Independently summed cost: {route_cost(GRAPH, result.path)}")
    print(f"Stale entries actually popped: {result.stale_ignored}")
    return result


def main() -> None:
    print("LAB 4 - INSTRUCTOR CAMPUS GRAPH")
    print("Graph:", GRAPH)
    print("Heuristic:", HEURISTIC)
    print("Tie-breaking: (f, g, node, path); successors in supplied order")
    print("Expansion: successors examined; goal logged but not counted")
    truth = shortest_remaining_costs(GRAPH, GOAL)
    print("\nHEURISTIC AUDIT: h(n) <= true remaining cost")
    for node in GRAPH:
        print(f"{node}: h={HEURISTIC[node]}, true_remaining={truth[node]}, admissible={HEURISTIC[node] <= truth[node]}")
    print("CONSISTENCY: h(u) <= weight + h(v)")
    for source, outgoing in GRAPH.items():
        for target, weight in outgoing:
            print(f"{source}->{target}: {HEURISTIC[source]} <= {weight}+{HEURISTIC[target]} = {weight + HEURISTIC[target]} : {HEURISTIC[source] <= weight+HEURISTIC[target]}")

    a = display_run("SUPPLIED HEURISTIC: A*", HEURISTIC)
    zeros = {node: 0 for node in GRAPH}
    u = display_run("ZERO HEURISTIC: UCS", zeros)
    modified = HEURISTIC.copy()
    modified["C"] = 10
    print("\nHEURISTIC CHANGE: C 2 -> 10; C true remaining cost = 3")
    b = display_run("OVER-ESTIMATE: A* WITH h(C)=10", modified)

    print("\nCOMPARISON")
    print(f"{'Experiment':<20} {'Path':<14} {'Cost':>5} {'Expanded':>8} {'Processed':>10}")
    for name, item in (("A* supplied", a), ("UCS zero-h", u), ("A* h(C)=10", b)):
        print(f"{name:<20} {'-'.join(item.path):<14} {item.reported_cost:>5} {item.expansion_count:>8} {len(item.processed):>10}")
    assert a.path == ["S", "A", "C", "G"] and a.reported_cost == 6 and a.expanded == ["S", "A", "C"]
    assert u.path == ["S", "A", "C", "G"] and u.reported_cost == 6 and u.expanded == ["S", "A", "C", "B"]
    assert b.path == ["S", "B", "G"] and b.reported_cost == 9 and b.expanded == ["S", "A", "B"]
    assert all(item.reported_cost == route_cost(GRAPH, item.path) for item in (a, u, b))
    assert all(HEURISTIC[node] <= truth[node] for node in GRAPH)
    assert all(HEURISTIC[src] <= weight + HEURISTIC[dst] for src in GRAPH for dst, weight in GRAPH[src])
    print("\nVerification: PASS - expected paths, independent costs, expansion traces, and heuristic audit")
    print("Note: UCS can leave a dominated G=9 entry pending when the better G=6 reaches the goal; it is not popped before termination.")


if __name__ == "__main__":
    main()
