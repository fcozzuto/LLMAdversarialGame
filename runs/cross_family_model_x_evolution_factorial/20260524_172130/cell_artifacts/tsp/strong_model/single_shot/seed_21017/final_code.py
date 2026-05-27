def build_heuristic():
    return {
        "name": "balanced_insertion_2opt",
        "strategy": "constructive_plus_local_search",
        "construction": {
            "type": "nearest_insertion",
            "seed_rule": "farthest_pair",
            "candidate_rule": "nearest_neighbors",
            "tie_break": "lexicographic"
        },
        "local_search": {
            "enabled": True,
            "moves": ["2-opt", "relocate"],
            "acceptance": "first_improvement",
            "max_passes": 5
        },
        "robustness": {
            "scale_invariant": True,
            "distance_normalization": "none",
            "heldout_transfer_bias": "balanced",
            "avoid_overfitting": True
        },
        "parameters": {
            "neighbor_k": 20,
            "insertion_sampling": 1,
            "candidate_pruning": "light",
            "restart_count": 0
        },
        "interpretability": {
            "simple_rules": True,
            "transparent_scoring": True
        }
    }
