def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "type": "tsp_heuristic_scaffold",
        "strategy": "nearest_neighbor_with_2opt_cleanup",
        "deterministic": True,
        "no_memory": True,
        "no_replay": True,
        "no_compression": True,
        "components": [
            {
                "name": "seed_selection",
                "method": "farthest_from_centroid",
                "tie_break": "lowest_index"
            },
            {
                "name": "construction",
                "method": "nearest_neighbor",
                "candidate_filter": "all_unvisited",
                "selection_rule": "minimum_increase",
                "tie_break": "lowest_index"
            },
            {
                "name": "local_search",
                "method": "2_opt",
                "first_improvement": True,
                "max_passes": 2,
                "accept_equal": False
            }
        ],
        "robustness_bias": {
            "prefer_geometric_structure": True,
            "avoid_instance_specific_tuning": True,
            "balanced_on_synthetic_and_tsplib": True
        },
        "parameters": {
            "construction_seed": "farthest_from_centroid",
            "two_opt_passes": 2
        }
    }
