def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for a constrained TSP heuristic with emphasis on robustness across held-out TSPLIB and synthetic transfer performance. Interpretable and not overly complex.",
        "technique": "failure_replay_compression",
        "assumptions": [
            "No replay archive entries available yet (Candidate 1).",
            "Constraints are specified externally and accessed via a consistent interface.",
            "Deterministic behavior is required for reproducibility."
        ],
        "parameters": {
            "preprocessing": {
                "remove_infeasible_edges": True,
                "normalize_distances": False,
                "build_adjacency_from_constraints": True
            },
            "construction": {
                "seed": 0,
                "method": "greedy_build_with_constraints",
                "priority_order": ["must_visit", "hard_constraint_edges", "geometric_proximity", "random_stability"],
                "max_degree": 3
            },
            "repair": {
                "enable": True,
                "strategy": "local_swap_then_backbone_fix",
                "limit": 100
            },
            "pruning": {
                "enable": True,
                "min_improvement_per_step": 0.001,
                "max_iterations": 50
            },
            "evaluation": {
                "score_components": ["feasibility", "constraint_satisfaction", "path_cost", "robustness_to_transfer"],
                "weights": {
                    "feasibility": 0.4,
                    "constraint_satisfaction": 0.3,
                    "path_cost": 0.2,
                    "robustness_to_transfer": 0.1
                }
            }
        },
        "data_interfaces": {
            "tsplib_loader": {
                "required_fields": ["name", "dimension", "edge_weights"],
                "supported_formats": ["tsplib", "custom"],
                "fallback": "synthetic"
            },
            "constraint_spec": {
                "type": "partial_order_or_capacity",
                "description": "Constraints on visiting order, vehicle capacity, or forbidden edges."
            }
        },
        "scalability": {
            "worst_case_time": "polynomial in number_of_nodes",
            "memory_footprint": "linear in number_of_edges plus constraint_set"
        },
        "robustness": {
            "transfer_friendly": True,
            "handles_missing_data": True,
            "deterministic_reproducibility": True
        },
        "notes": [
            "This scaffold favors interpretability: explicit greedy-with-repair steps and simple pruning.",
            "Failure_replay_compression refers to a deterministic replay-like strategy; since no archives exist, this scaffold operates in a no-archive mode."
        ]
    }
