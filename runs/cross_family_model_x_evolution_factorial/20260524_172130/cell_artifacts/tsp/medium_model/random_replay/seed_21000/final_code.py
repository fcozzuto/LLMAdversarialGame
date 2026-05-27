def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic, interpretable TSP heuristic scaffold with constrained transfer evaluation. Uses a simple, robust approach suitable for held-out TSPLIB and synthetic transfer tests.",
        "technique": "random_replay",
        "parameters": {
            "seed": 0,
            "init_route_method": "nearest_neighbor",
            "segment_constraints": [
                {
                    "type": "subtour_elimination",
                    "method": "2-opt_like",
                    "max_subtour_size": 2
                }
            ],
            "exchange_operations": [
                {"op": "swap", "scope": "adjacent", "limit": 2},
                {"op": "reinsert", "limit": 2}
            ],
            "termination": {
                "criterion": "distance_improvement_threshold",
                "threshold": 1e-6,
                "max_iterations": 250
            }
        },
        "scoring": {
            "primary": "total_distance",
            "secondary": ["constraint_violations", "balance_of_visit_counts"],
            "penalties": {
                "unconstrained_violation": 1e6,
                "high_degree_node": 100.0
            },
            "normalization": {
                "normalize_by_nodes": True
            }
        },
        "transfer_considerations": {
            "held_out_tsplib": {
                "reference_sets": ["pr106", "att48", "eil76", "kroA100"],
                "evaluation_metric": "relative_improvement",
                "max_transfer_scale": 1.0
            },
            "synthetic_transfer": {
                "generation": "same_geometry_transform",
                "noise_level": 0.0,
                "transfer_fraction": 0.5
            }
        },
        "robustness": {
            "deterministic_seed": 0,
            "repeatable_runs": True,
            "fallbacks": [
                {
                    "condition": "no_improvement",
                    "action": "terminate_and_return_best"
                }
            ]
        },
        "interpretability": {
            "route_representation": "sequence_of_node_indices",
            "constrains_explained": True,
            "log_messages": False
        },
        "architecture": {
            "components": [
                {"name": "initialization", "description": "greedy nearest neighbor with fixed seed"},
                {"name": "local_search", "description": "limited 2-opt-like neighborhood with subtour checks"},
                {"name": "constrained_moves", "description": "swap and reinsert with simple constraint handling"},
                {"name": "transfer_evaluation", "description": "assess performance on held-out and synthetic sets"}
            ],
            "explanation": "The scaffold is intentionally simple and interpretable, enabling deterministic replay of candidate tours and straightforward evaluation across held-out TSPLIB instances and synthetic transfers."
        }
    }
