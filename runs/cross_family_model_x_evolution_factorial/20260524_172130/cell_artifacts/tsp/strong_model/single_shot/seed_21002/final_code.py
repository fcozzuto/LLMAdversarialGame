def build_heuristic():
    return {
        "technique": "single_shot",
        "candidate": 1,
        "problem": "constrained_tsp",
        "objective": "robust_transfer",
        "design_principles": [
            "interpretability",
            "determinism",
            "simple_components",
            "held_out_generalization",
        ],
        "construction": {
            "initial_tour": "nearest_neighbor_with_feasibility_filter",
            "seed_policy": "choose_best_of_fixed_start_set",
            "start_set": "extreme_and_central_nodes",
            "candidate_rule": "prefer feasible edges with low distance and low insertion disruption",
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": [
                "constraint_slack_penalty",
                "late_violation_penalty",
                "crossing_penalty",
            ],
            "weights": {
                "tour_length": 1.0,
                "constraint_slack_penalty": 0.3,
                "late_violation_penalty": 0.8,
                "crossing_penalty": 0.2,
            },
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "relocate", "swap"],
            "acceptance": "first_improvement",
            "move_budget": "small_fixed_budget",
        },
        "repair": {
            "enabled": True,
            "strategy": "feasibility_first_insertion_then_shorten",
        },
        "transfer_bias": {
            "favor_regularization_over_instance_specific_tuning": True,
            "avoid_overfitting_to_coordinate_scale": True,
            "normalize_distances": True,
        },
        "stopping": {
            "deterministic_budget": True,
            "budget_type": "fixed_iterations",
            "iterations": 200,
        },
    }
