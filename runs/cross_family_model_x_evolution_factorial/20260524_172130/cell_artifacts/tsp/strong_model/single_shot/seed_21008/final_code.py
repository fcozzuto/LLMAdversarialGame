def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "problem": "tsp",
        "style": "interpretable_heuristic_scaffold",
        "strategy": {
            "construction": "nearest_neighbor_with_lookahead",
            "lookahead_depth": 2,
            "insertion_rule": "minimize_increase_with_tie_break_by_shorter_edge",
            "local_search": [
                "2-opt",
                "simple_or-opt"
            ],
            "restart_policy": {
                "enabled": False,
                "count": 1
            }
        },
        "robustness": {
            "favor_generalization": True,
            "held_out_transfer": True,
            "synthetic_transfer": True,
            "scale_invariance": True,
            "coordinate_normalization": True
        },
        "interpretability": {
            "explainable_steps": True,
            "bounded_complexity": True,
            "avoid_black_box": True
        },
        "parameters": {
            "candidate_pool_size": 8,
            "two_opt_max_passes": 3,
            "or_opt_segment_lengths": [1, 2],
            "tie_breaks": [
                "shortest_edge",
                "lowest_index"
            ]
        }
    }
