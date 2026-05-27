def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic using a "random_replay" style approach.
    # This scaffold is lightweight, interpretable, and does not rely on imports.
    # It emphasizes robustness across held-out TSPLIB-like instances and synthetic transfers.
    heuristic = {
        "name": "random_replay_constrained_tsp_scaffold",
        "version": 1,
        "description": "Deterministic constrained TSP heuristic scaffold with random_replay flavor but no external data.",
        "technique": "random_replay",
        "policy": {
            "initial_solution": {
                "method": "nearest_neighbor",
                "seed": 0,  # deterministic seed for reproducibility
                "start_node": 0
            },
            "constraints": {
                "max_time": 1.0,            # seconds (synthetic cap)
                "max_distance": None,        # no explicit path-length cap
                "subtour_elimination": True,   # ensure Hamiltonian cycle
                "visit_once": True              # each node visited exactly once
            },
            "replay": {
                "archive_used": False,          # no replay archive available yet
                "replay_count": 0,
                "seed": 0
            },
            "selection": {
                "strategy": "greedy_by_feasibility",  # prefer feasible, low-cost steps
                "lookahead": 0,                        # no lookahead to keep it simple
                "tie_breaker": "node_index"             # deterministic tie-breaking
            },
            "improvement": {
                "local_search": False,                  # disable heavyweight LS to keep interpretability
                "local_search_iterations": 0
            },
            "transfer_support": {
                "enable_synthetic_transfer": True,
                "transfer_metric": "relative_cost_gain",
                "risk_assessment": False
            },
            "robustness": {
                "holdout_considerations": True,
                "out_of_domain_checks": True,
                "fallback_policy": "return_initial_solution"  # deterministic fallback
            }
        },
        "data_schema": {
            "instance_label": "string",
            "node_count": "int",
            "edge_costs": "2D_array_float",
            "constraints": "dict_optional",
            "seed": "int"
        },
        "expected_behavior": {
            "stable_outputs": True,
            "deterministic": True,
            "scalability": "linearithmic_in_n"  # coarse expectation for robustness
        },
        "notes": [
            "This scaffold is intentionally simple and deterministic.",
            "No imports are used; all logic is self-contained.",
            "Geared toward evaluating robustness across held-out TSPLIB-like instances and synthetic transfers without replay archive data."
        ]
    }
    return heuristic
