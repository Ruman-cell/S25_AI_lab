

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class MinimaxResult:
    value: int
    evaluated_leaves: int
    evaluated_nodes: list[str] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)


def prepare_scores(scores: list[int]) -> tuple[list[int], int]:
    """Pad scores with zeros to the next power of two, as required by the lab."""
    if not scores:
        raise ValueError("scores must contain at least one utility value")
    depth = math.ceil(math.log2(len(scores))) if len(scores) > 1 else 0
    leaf_count = 2**depth
    return scores + [0] * (leaf_count - len(scores)), depth


def minimax(scores: list[int], depth: int, maximizing_player: bool = True) -> MinimaxResult:
    
    expected = 2**depth
    if len(scores) != expected:
        raise ValueError(f"depth {depth} requires exactly {expected} leaves")

    trace: list[str] = []
    visited: list[str] = []
    leaf_count = 0

    def search(level: int, index: int, maximizing: bool, path: str) -> int:
        nonlocal leaf_count
        indent = "  " * level
        node_type = "MAX" if maximizing else "MIN"

        if level == depth:
            value = scores[index]
            leaf_count += 1
            visited.append(f"{path}={value}")
            trace.append(f"{indent}Leaf {path}: utility = {value}")
            return value

        trace.append(f"{indent}{node_type} node {path}:")
        left = search(level + 1, index * 2, not maximizing, path + "L")
        right = search(level + 1, index * 2 + 1, not maximizing, path + "R")
        value = max(left, right) if maximizing else min(left, right)
        operation = "max" if maximizing else "min"
        trace.append(
            f"{indent}{node_type} {path} = {operation}({left}, {right}) = {value}"
        )
        return value

    root_value = search(0, 0, maximizing_player, "Root")
    return MinimaxResult(root_value, leaf_count, visited, trace)


def main() -> None:
    original_scores = [3, 5, 2, 9, 0, 7]
    padded_scores, depth = prepare_scores(original_scores)
    result = minimax(padded_scores, depth)

    print("MINIMAX - INSTRUCTOR REFERENCE")
    print(f"Original scores: {original_scores}")
    print(f"Tree depth: {depth}")
    print(f"Padded leaves: {padded_scores}")
    print("\nStep-by-step trace:")
    print("\n".join(result.trace))
    print(f"\nEvaluated nodes: {', '.join(result.evaluated_nodes)}")
    print(f"Root value: {result.value}")
    print(f"Leaf evaluations: {result.evaluated_leaves}")
    print("Pruned branches: none (plain Minimax does not prune)")


if __name__ == "__main__":
    main()
