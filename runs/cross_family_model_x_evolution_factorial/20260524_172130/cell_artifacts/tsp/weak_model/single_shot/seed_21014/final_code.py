def build_heuristic():
    return {
        "technique": "single_shot",
        "candidate": 1,
        "description": "A simple deterministic heuristic for constrained TSP based on a nearest-neighbor approach with adjustments for constraints.",
        "parameters": {
            "initial_node": "min_node",  # start from the node with the smallest index for consistency
            "neighbor_selection": "nearest_with_feasibility",  # pick nearest feasible neighbor
            "feasibility_check": "capacity_constraint_only",  # only check capacity constraints
            "path_extension": "greedy",  # extend path greedily
            "termination": "all_nodes_visited",  # stop when all nodes are visited
            "constraint_tolerance": 0  # strict adherence to constraints
        },
        "heuristic_steps": [
            "Select starting node deterministically as node with minimum index.",
            "Iteratively select the nearest neighbor to the current node that satisfies capacity constraints.",
            "Append selected node to the path.",
            "Repeat until all nodes are visited.",
            "Return the constructed route as the heuristic solution."
        ],
        "robustness": "Designed for solving a wide range of TSPLIB instances with capacity constraints, balancing simplicity and performance.",
        "interpretability": "Uses a standard nearest-neighbor approach with explicit feasibility checks, making the heuristic transparent and easy to understand.",
        "complexity": "O(n^2) per run, suitable for moderate size problems."
    }

