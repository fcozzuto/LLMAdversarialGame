def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "mode": "deterministic_tsp_heuristic_scaffold",
        "design_principles": [
            "interpretable",
            "robust_transfer",
            "lightweight",
            "failure_replay_ready",
        ],
        "construction": {
            "method": "nearest_neighbor",
            "start_policy": "multi_start_deterministic",
            "start_nodes": ["min_x", "max_x", "min_y", "max_y", "centroid_nearest"],
            "tie_break": "lowest_index",
        },
        "improvement": {
            "primary": "2-opt",
            "secondary": "limited_3-opt",
            "candidate_filter": "nearest_neighbors",
            "k_neighbors": 20,
            "first_improvement": True,
            "max_passes": 4,
        },
        "perturbation": {
            "method": "segment_reversal",
            "strength": "small",
            "enabled": True,
        },
        "replay_compression": {
            "enabled": True,
            "archive_capacity": 0,
            "entry_type": "none",
            "compression": "pattern_only",
            "use_on_failure": True,
        },
        "selection": {
            "objective": "tour_length",
            "accept_only_improving": True,
            "deterministic_restart_order": True,
        },
        "fallbacks": {
            "if_local_search_stalls": "try_next_start_node",
            "if_all_starts_equal": "return_best_constructed",
        },
    }
