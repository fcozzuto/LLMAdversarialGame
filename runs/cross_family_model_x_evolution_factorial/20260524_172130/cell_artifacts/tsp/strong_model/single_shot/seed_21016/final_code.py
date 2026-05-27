def build_heuristic():
    return {
        "name": "robust_interpretable_tsp_scaffold",
        "problem": "tsp",
        "technique": "single_shot",
        "candidate": 1,
        "deterministic": True,
        "objective": "minimize_tour_length",
        "representation": "permutation",
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": "lowest_index",
            "seedless": True
        },
        "improvement": {
            "primary": "2-opt",
            "secondary": "3-opt_limited",
            "secondary_limit": 1,
            "acceptance": "strict_improvement",
            "sweep_order": "best_first",
            "stop_rule": "no_improvement"
        },
        "diversification": {
            "enabled": False,
            "reason": "single_shot_interpretable_scaffold"
        },
        "transfer_bias": {
            "favor": [
                "sparse_candidate_edges",
                "metric_agnostic_local_search",
                "scale_invariant_decisions"
            ],
            "avoid": [
                "instance_specific_tuning",
                "memorization",
                "deep_search"
            ]
        },
        "robustness": {
            "target": [
                "TSPLIB",
                "synthetic_euclidean",
                "synthetic_non_euclidean"
            ],
            "notes": "Use a simple greedy start followed by bounded local search for stable cross-instance behavior."
        },
        "parameters": {
            "candidate_list_size": 20,
            "max_2opt_passes": 50,
            "max_3opt_moves": 25,
            "distance_policy": "use_problem_distance",
            "numerical_stability": "prefer_integer_comparisons_when_possible"
        },
        "output": {
            "type": "tour",
            "canonicalize": True
        }
    }
