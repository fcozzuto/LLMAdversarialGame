def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "type": "tsp_heuristic_scaffold",
        "candidate": 1,
        "deterministic": True,
        "no_replay": True,
        "no_memory": True,
        "no_compression": True,
        "goal": "robust_transfer",
        "priority": [
            "held_out_TSPLIB",
            "synthetic_transfer",
            "interpretability",
            "stability",
        ],
        "construction": {
            "seed_tour": "nearest_neighbor",
            "start_policy": "best_of_few_deterministic_starts",
            "start_count": 5,
            "candidate_rule": "nearest_unvisited_with_tie_break_by_lowest_index",
        },
        "improvement": {
            "local_search": ["2-opt", "node_relocation"],
            "acceptance": "strict_improvement_only",
            "max_passes": 3,
            "budget_matching": True,
        },
        "budget_matching": {
            "target": "match_improvement_budget_to_instance_size",
            "small_instance_cap": 200,
            "medium_instance_cap": 1000,
            "large_instance_cap": 5000,
            "scale_rule": "linear_with_soft_cap",
        },
        "tie_breaking": {
            "distance": "lowest",
            "index": "lowest",
            "consistency": "lexicographic",
        },
        "robustness": {
            "symmetric": True,
            "scale_invariant": True,
            "uses_coordinates_only": True,
            "avoids_overfitting_signals": True,
        },
        "output": {
            "tour_representation": "permutation",
            "cost_metric": "total_euclidean_length",
        },
    }
