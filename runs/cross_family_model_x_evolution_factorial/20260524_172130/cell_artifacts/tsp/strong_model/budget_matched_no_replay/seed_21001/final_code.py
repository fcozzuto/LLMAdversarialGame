def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "version": 1,
        "type": "tsp_heuristic_scaffold",
        "deterministic": True,
        "no_replay": True,
        "no_prior_candidates": True,
        "no_memory": True,
        "no_compression": True,
        "design_goals": [
            "robust_transfer",
            "interpretable",
            "budget_matched",
            "constrained_tsp"
        ],
        "construction": {
            "initial_tour": "nearest_neighbor",
            "seed_policy": "farthest_start",
            "candidate_list_size": 20,
            "distance_metric": "euclidean_or_given_cost",
            "tie_break": "lexicographic"
        },
        "improvement": {
            "local_search": [
                "2-opt",
                "relocate"
            ],
            "acceptance": "strict_improvement",
            "max_passes": 3,
            "move_budget": "matched_to_instance_size",
            "budget_rule": {
                "base_factor": 2.0,
                "cap_factor": 10.0,
                "scale_with_n": True
            }
        },
        "constraint_handling": {
            "method": "penalty_then_repair",
            "repair": [
                "remove_crossings",
                "feasible_insertion"
            ],
            "penalty_weight": 1000
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": "constraint_violation",
            "lexicographic": True
        },
        "robustness": {
            "prefer_balanced_edges": True,
            "avoid_overfitting_specific_geometries": True,
            "use_instance_normalization": True
        }
    }
