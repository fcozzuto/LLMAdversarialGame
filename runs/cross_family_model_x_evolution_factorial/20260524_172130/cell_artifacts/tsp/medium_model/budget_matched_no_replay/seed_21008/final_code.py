def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic using a budget-matched_no_replay approach.
    # This dictionary encodes parameters and components in a readable, interpretable way.
    return {
        "name": "budget_matched_no_replay_candidate_1",
        "description": (
            "Deterministic constrained TSP heuristic scaffold with budget-matched heuristic components, "
            "no replay memory, no failure memory, no compression. Emphasizes robustness across TSPLIB "
            "held-out instances and synthetic transfers."
        ),
        "criterion": {
            "objective": "minimize_distance_with_constraint_violation_rate",
            "constraints": {
                "max_runtime_seconds": 5.0,
                "max_memory_mb": 256,
                "max_violation_fraction": 0.0
            }
        },
        "instances": {
            "held_out_tsplib": True,
            "synthetic_transfer": True,
            "training_influence": "balanced",
            "seed": 42
        },
        "components": {
            # Deterministic, interpretable building blocks
            "initialization": {
                "method": "nearest_neighbor_with_seed",
                "seed_node": "min_degree_node",
                "distance_metric": "euclidean",
                "preprocessing": ["normalize_coordinates"]
            },
            "construction": {
                "strategy": "greedy_feasible_extension",
                "budget_control": {
                    "budget_fraction": 0.9,  # fraction of tour length allowed to be built before pruning
                    "prune_when": "local_improvement_threshold"
                },
                "feasibility_checks": [
                    "subtour_elimination",
                    "degree_constraint"
                ],
                "tie_breaker": "lowest_incremental_cost"
            },
            "local_search": {
                "enabled": True,
                "method": "2_opt",
                "iterations": 50,
                "adaptation": {
                    "no_replay": True,
                    "memory_size": 0
                }
            },
            "transfer_and_transfer_learning": {
                "enabled": True,
                "ratio_augmentation": 0.15,
                "domain_shifts": ["size_scaling", "coordinate_permutation"],
                "fallback_to_host_instance_quality": "average"
            },
            "robustness_and_validation": {
                "cross_validation": False,
                "hold_out_validation": True,
                "confidence_threshold": 0.0
            }
        },
        "metrics": {
            "primary": "tour_length",
            "secondary": ["feasibility_rate", "runtime"],
            "evaluation_plan": {
                "per_instance": ["edge_count", "degree_distribution"],
                "aggregate": ["mean_tour_length", "std_tour_length", "violation_rate"]
            }
        },
        "dependencies": {
            "memory_management": "preallocated_buffers",
            "reproducibility": "fixed_seed_determinism",
            "output_format": "plain_dict_for_traceability"
        }
        ,
        "notes": "Deterministic scaffold emphasizing robustness across held-out TSPLIB and synthetic transfer with budgeted search, no replay memory."
    }
