def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "version": 1,
        "candidate": 1,
        "properties": {
            "deterministic": True,
            "interpretable": True,
            "no_replay": True,
            "no_memory": True,
            "transfer_focus": True,
        },
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": ["shorter_edge", "lower_index"],
            "candidate_filter": {
                "use_k_nearest": 12,
                "include_unvisited_only": True,
            },
            "cost": {
                "primary": "euclidean_distance",
                "secondary": "lookahead_penalty",
                "lookahead_depth": 2,
                "lookahead_weight": 0.15,
            },
        },
        "improvement": {
            "method": "two_opt",
            "budget_model": "budget_matched",
            "max_passes": 3,
            "max_swaps_per_pass": 64,
            "accept_only_improving": True,
            "segment_filter": {
                "skip_adjacent_edges": True,
                "prefer_long_edges_first": True,
            },
        },
        "robustness": {
            "scale_invariant": True,
            "translation_invariant": True,
            "works_on_synthetic": True,
            "works_on_tsplib": True,
        },
        "fallbacks": {
            "if_candidate_set_empty": "nearest_unvisited",
            "if_no_improvement": "return_current_tour",
        },
    }
