def build_heuristic():
    return {
        "name": "interpretable_tsp_heuristic",
        "technique": "single_shot",
        "candidate": 1,
        "deterministic": True,
        "no_memory": True,
        "objective": "minimize_tour_length",
        "transfer_focus": ["held_out_tsplib", "synthetic_instances"],
        "construction": {
            "method": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": "lowest_index",
        },
        "improvement": {
            "method": "2_opt",
            "acceptance": "strict_improvement",
            "candidate_filter": "donot_consider_crossing_edges_first",
            "max_passes": 10,
            "early_stop_no_improve": 2,
        },
        "restart": {
            "enabled": True,
            "count": 3,
            "start_points": ["farthest_from_centroid", "lexicographic_min", "lexicographic_max"],
        },
        "robustness": {
            "normalize_coordinates": True,
            "distance_metric": "euclidean",
            "use_full_precision": True,
            "avoid_instance_specific_tuning": True,
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": "edge_crossings",
            "tertiary": "locality_preservation",
        },
        "constraints": {
            "respect_input_order": False,
            "no_randomness": True,
            "interpretable": True,
            "not_overly_complex": True,
        },
    }
