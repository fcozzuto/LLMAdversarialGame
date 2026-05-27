def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic using budget_matched_no_replay approach.
    # No external imports. Returns a dictionary describing the heuristic components and defaults.
    return {
        "name": "budget_matched_no_replay_scheme",
        "version": 1,
        "description": "Deterministic constrained TSP heuristic scaffold with budget matching and no replay.",
        "technique": "budget_matched_no_replay",
        "memory_policy": {
            "use_replay_memory": False,
            "use_failure_memory": False,
            "budget_controls": True
        },
        "budget_management": {
            "budget_source": "static_budget_per_instance",
            "budget_allocation": "equal_split_by_node_count",
            "budget_adjustment": "none"  # deterministic, no adaptation
        },
        "transfers": {
            "mode": "transfer_defaults",
            "transfer_performance": "synthetic_and_tsplib_robust",
            "transfer_order": "synthetic_then_tsplib"
        },
        "constrains": {
            "type": "geometric_and_capacity",
            "node_capacity": "uniform",
            "edge_constraints": {
                "mandatory_edges": [],
                "forbidden_edges": []
            }
        },
        "heuristic_core": {
            "planner": "greedy_incremental_with_budget",
            "local_search": "2opt",
            "tie_breaking": "lexicographic",
            "stopping_criteria": {
                "iterations": 100,
                "improvement_threshold": 1e-6
            }
        },
        "robustness": {
            "scenarios": [
                "TSPLIB_benchmarks",
                "synthetic_transfer_sets"
            ],
            "evaluation": {
                "metrics": ["tour_length", "violation_penalty", "runtime"],
                "parity_checks": True
            }
        },
        "interpretability": {
            "parameters_exposed": [
                "budget_split_per_node",
                "edge_penalty_factor",
                "greedy_step_size",
                "search_radius"
            ],
            "documentation": "Deterministic scaffold with clear budget controls and simple local search."
        },
        "defaults": {
            "budget_split_per_node": 1.0,
            "edge_penalty_factor": 1.0,
            "greedy_step_size": 1,
            "search_radius": None
        }
    }
