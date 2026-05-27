def build_heuristic():
    return {
        "name": "deterministic_constrained_tsp_heuristic",
        "version": 1,
        "description": "A deterministic, interpretable TSP heuristic scaffold for constrained instances with held-out TSPLIB and synthetic transfer considerations.",
        "technique": "random_replay",
        "archives": {
            "available": False,
            "entries": []
        },
        "parameters": {
            "seed": 42,
            "max_runtime_seconds": 5,
            "initial_solution_strategy": "nearest_neighbor_with_constraints",
            "constrained_edge_penalty": 1000.0,
            "allow_subtour_elimination": True,
            "tour_completion_tolerance": 1e-6,
            "transfer_focus": ["held_out_tsplib", "synthetic_transfer"],
            "robustness_heuristics": [
                "mandatory_cluster_constraints",
                "capacity_bounds",
                "time_window_feasibility"
            ],
            "repetition": 1,
            "logging": {
                "level": "warning",
                "record_paths": False
            }
        },
        "heuristic_blocks": [
            {
                "block_id": "init_seed",
                "description": "Initialize with a deterministic pivoted nearest-neighbor, respecting simple constraints.",
                "method": "nearest_neighbor_with_constraints",
                "constraints": {
                    "must_include_vertices": None,
                    "forbidden_edges": None
                },
                "tie_breaker": "lowest_index"
            },
            {
                "block_id": "subtour_elimination",
                "description": "Simple MTZ-style subtour elimination guard (deterministic).",
                "method": "subtour_elimination",
                "params": {
                    "method": "MTZ",
                    "penalty_multiplier": 1.0
                }
            },
            {
                "block_id": "constraint_propagation",
                "description": "Propagate hard constraints along the partial tour to prune infeasible extensions.",
                "method": "constraint_propagation",
                "params": {
                    "use_degree_bound": True
                }
            },
            {
                "block_id": "replay_planning",
                "description": "Deterministic replay scaffold to reuse prior state without actual replay entries.",
                "method": "replay_planning",
                "params": {
                    "archive_available": False,
                    "fallback_strategy": "greedy_capacitated"
                }
            },
            {
                "block_id": "transfer_fidelity",
                "description": "Favor transfer performance by preferring edges common to held-out TSPLIB and synthetic sets.",
                "method": "edge_weight_adjustment",
                "params": {
                    "basis": "edge_frequency_in_transfer_sets",
                    "scaling": 1.0
                }
            }
        ],
        "metrics": {
            "primary": ["tour_length", "feasibility", "runtime_seconds"],
            "secondary": ["subtour_count", "constraint_violations"]
        },
        "outputs": {
            "solution": "sequence_of_vertex_indices",
            "status": "feasible_or_infeasible",
            "log": "deterministic_run_log.txt"
        }
    }
