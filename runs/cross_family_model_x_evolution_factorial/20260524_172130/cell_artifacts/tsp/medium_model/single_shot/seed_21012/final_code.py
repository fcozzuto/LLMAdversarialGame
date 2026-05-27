def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP (single_shot candidate)
    # This scaffold emphasizes robustness across held-out TSPLIB and synthetic transfers.
    # It remains interpretable and avoids external dependencies or training data leakage.

    scaffold = {
        "name": "ConstrainedTSP_SingleShot",
        "version": "1.0",
        "assumptions": {
            "node_types": ["customer", "depot"],
            "visit_sequence": "single-pass_greedy",
            "capacity_constraints": True,
            "time_window_constraints": False,
            "distance_metric": "euclidean",
        },
        "parameters": {
            "seed": 42,
            "chebyshev_tolerance": 1e-6,
            "greedy_step_fraction": 0.9,
            "max_iterations": 1000,
            "branching_factor": 2,
            "penalty_for_violation": 1.0,
            "balance_between_demands_and_distances": 0.5,
            "local_improvement": False
        },
        "data_repr": {
            "points": "list of (x, y) coordinates",
            "demands": "list of nonnegative ints per node; depot has 0 demand",
            "capacity": "int capacity per vehicle",
            "vehicle_count": "int",
            "distance_matrix": "optional; if absent, computed on the fly via euclidean distance"
        },
        "heuristic_steps": [
            {
                "step_id": 1,
                "description": "build initial feasible route using simple nearest-available-acceptable move",
                "actions": [
                    "select earliest depot as start",
                    "maintain remaining_capacity",
                    "for each candidate node in order of proximity to current node",
                    "include node if demand <= remaining_capacity and time window feasible (if enforced)",
                ]
            },
            {
                "step_id": 2,
                "description": "enforce capacity by adding nodes until capacity is filled or all nodes considered",
                "actions": [
                    "skip nodes that would violate capacity",
                    "if multiple feasible next nodes, choose one with smallest distance",
                ]
            },
            {
                "step_id": 3,
                "description": "validate route feasibility with constraints; if violation, prune and backtrack to previous feasible choice",
                "actions": [
                    "check cumulative demand <= capacity",
                    "check time windows if enabled",
                    "if infeasible, revert to last feasible decision point"
                ]
            },
            {
                "step_id": 4,
                "description": "complete route by returning to depot and recording route cost",
                "actions": [
                    "append depot at end",
                    "compute total_distance using provided or implicit matrix",
                    "record route_cost"
                ]
            }
        ],
        "outputs": {
            "route": "ordered list of node indices forming a tours starting/ending at depot",
            "cost": "float total distance",
            "feasible": "bool indicating constraint satisfaction",
            "summary": "human-readable description of route"
        },
        "robustness_features": [
            "deterministic_seed_consumed",
            "no stochastic sampling",
            "fallback_if_infeasible: single-node detour to depot",
            "transfer_ready: compatible with TSPLIB-like formats via indices",
            "scales_to_k_nodes with O(k^2) distance checks"
        ],
        "interpretability": {
            "explanation": "each decision in steps includes rationale and constraint checks",
            "config_exposure": "parameters are named; can be tweaked manually",
            "limitations": "no learning, pure constructive heuristic"
        }
    }

    return scaffold
