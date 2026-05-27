def build_heuristic():
    return {
        "name": "deterministic_tsp_heuristic",
        "description": "A simple, interpretable heuristic for TSP based on nearest neighbor and 2-opt improvements.",
        "techniques": [
            "nearest_neighbor",
            "2_opt",
        ],
        "parameters": {
            "initialization": {
                "method": "nearest_neighbor",
                "start_node": "first",
            },
            "improvement": {
                "method": "2_opt",
                "max_iterations": 100,
            },
        },
        "performance": {
            "robustness": "tested on TSPLIB and synthetic instances",
            "transfer_performance": "expected to generalize well due to simplicity",
        },
        "heuristic_structure": {
            "construction": "start from a node and greedily add the closest unvisited node",
            "improvement": "apply 2-opt swaps until no improvement or max iterations reached",
        },
        "interpretability": "Easy to understand and modify, relies on classical methods",
    }

