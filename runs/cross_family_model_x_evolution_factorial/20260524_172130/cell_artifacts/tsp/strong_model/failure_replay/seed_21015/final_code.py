def build_heuristic():
    return {
        "technique": "failure_replay",
        "candidate": 1,
        "replay_archive": [],
        "heuristic": {
            "name": "robust_candidate_insertion_2opt",
            "description": "Deterministic constructive tour with nearest-neighbor seeding, regret-2 insertion, and limited 2-opt cleanup.",
            "construction": {
                "seed_rule": "start_from_lowest_index_city",
                "initialization": "nearest_neighbor",
                "insertion_rule": "regret_2",
                "tie_break": "lowest_index",
            },
            "improvement": {
                "local_search": "2_opt",
                "move_budget": "bounded",
                "acceptance": "first_improvement",
                "edge_filters": ["crossing_removal", "short_gain_only"],
            },
            "robustness": {
                "normalize_distances": False,
                "prefer_sparse_geometric_structure": True,
                "avoid_instance_specific_features": True,
                "generalize_to_metric_and_near_metric": True,
            },
            "parameters": {
                "max_2opt_passes": 3,
                "regret_k": 2,
                "candidate_list_size": 12,
            },
        },
    }
