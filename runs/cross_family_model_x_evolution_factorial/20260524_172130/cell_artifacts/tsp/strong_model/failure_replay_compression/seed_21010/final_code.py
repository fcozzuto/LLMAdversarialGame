def build_heuristic():
    return {
        "name": "failure_replay_compression_candidate_1",
        "problem": "TSP",
        "objective": "minimize_tour_length",
        "strategy": {
            "type": "construct_and_improve",
            "construction": {
                "method": "nearest_neighbor_multi_start",
                "starts": ["min_x", "max_x", "min_y", "max_y"],
                "tie_break": "lexicographic",
            },
            "improvement": {
                "method": "2-opt",
                "candidate_filter": "don_t_consider_adjacent_edges",
                "acceptance": "first_improvement",
                "max_passes": 20,
            },
            "postprocess": {
                "method": "tour_rotation_normalization",
                "canonical_start": "smallest_node_id",
            },
        },
        "robustness": {
            "held_out_focus": True,
            "synthetic_transfer": True,
            "use_geometry_only": True,
            "scale_invariant": True,
            "translation_invariant": True,
            "rotation_invariant": True,
        },
        "failure_replay_compression": {
            "enabled": True,
            "archive_entries": 0,
            "compression_policy": "retain_only_action_patterns_not_instance_specific_overrides",
        },
        "interpretability": {
            "complexity": "low",
            "notes": [
                "Simple geometric starts improve coverage across instance shapes.",
                "2-opt provides a strong, transparent local search baseline.",
                "No learned parameters or opaque scoring rules.",
            ],
        },
    }
