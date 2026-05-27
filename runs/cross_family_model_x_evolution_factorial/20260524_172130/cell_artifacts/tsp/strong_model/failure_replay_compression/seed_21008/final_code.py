def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "type": "tsp_heuristic_scaffold",
        "goal": "robust_transfer_on_held_out_tsplib_and_synthetic_instances",
        "properties": {
            "deterministic": True,
            "interpretable": True,
            "complexity": "moderate",
            "archive_available": False
        },
        "construction": {
            "initial_tour": "nearest_neighbor_multi_start",
            "start_selection": "farthest_point_set",
            "candidate_filter": "k_nearest_neighbors",
            "construction_tie_break": "lowest_increase_then_shortest_edge",
            "fallback": "greedy_insertion"
        },
        "local_search": {
            "primary": ["2-opt", "or-opt-1"],
            "secondary": ["3-opt_limited"],
            "move_acceptance": "strict_improvement",
            "termination": "no_improvement_pass"
        },
        "compression": {
            "method": "failure_replay_compression",
            "representation": "compact_edge_failure_notes",
            "action": "avoid_repeated_bad_swap_patterns",
            "memory_limit": 32,
            "applies_to": ["construction", "local_search"]
        },
        "scoring": {
            "edge_cost": "euclidean",
            "penalties": {
                "crossings": 1.5,
                "long_tour_edges": 1.0,
                "repeated_failures": 2.0
            }
        },
        "robustness": {
            "scale_normalization": True,
            "coordinate_translation_invariant": True,
            "coordinate_rotation_invariant": True,
            "prefers_sparse_updates": True
        },
        "parameters": {
            "multi_start_count": 4,
            "candidate_list_size": 12,
            "max_3opt_trials": 64,
            "insertion_restarts": 2
        }
    }
