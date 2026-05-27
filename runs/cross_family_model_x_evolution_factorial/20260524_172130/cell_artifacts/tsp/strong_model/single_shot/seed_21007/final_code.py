def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "problem": "constrained_tsp",
        "style": "interpretable_heuristic_scaffold",
        "deterministic": True,
        "no_learning": True,
        "no_memory": True,
        "candidate_id": 1,
        "technique": "single_shot",
        "objective_bias": {
            "primary": "short_tour_length",
            "secondary": "constraint_feasibility",
            "tertiary": "transfer_robustness"
        },
        "construction": {
            "seed_policy": "nearest_to_centroid",
            "initial_tour": "nearest_neighbor",
            "tie_break": "lexicographic",
            "candidate_filter": "feasible_only"
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "or-opt-1", "swap"],
            "move_order": ["2-opt", "or-opt-1", "swap"],
            "acceptance": "strict_improvement",
            "restart": "single_pass"
        },
        "constraint_handling": {
            "method": "penalty_plus_repair",
            "repair_priority": ["time_window", "capacity", "precedence"],
            "penalty_schedule": "fixed",
            "infeasible_move_policy": "reject"
        },
        "robustness": {
            "instance_scaling_invariant": True,
            "uses_coordinate_geometry": True,
            "uses_distance_rankings": True,
            "avoids_instance_specific_constants": True
        },
        "transfer_bias": {
            "prefer": ["low_regret_insertions", "short_edges", "balanced_crossings_reduction"],
            "avoid": ["deep_backtracking", "overfitted_patterns"]
        },
        "stopping": {
            "max_passes": 2,
            "max_no_improve": 1
        },
        "output": {
            "representation": "ordered_city_sequence",
            "validate_feasibility": True
        }
    }
