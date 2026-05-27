def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "problem": "TSP",
        "deterministic": True,
        "goal": "robust held-out TSPLIB and synthetic transfer performance",
        "interpretability": "high",
        "complexity": "moderate",
        "construction": {
            "method": "nearest_neighbor_multi_start",
            "starts": "fixed_set",
            "start_rule": "farthest_pair_seed_then_extend",
            "tie_break": "lowest_index"
        },
        "improvement": {
            "method": "2-opt",
            "move_order": "best_improvement",
            "candidate_list": "nearest_neighbors",
            "candidate_k": 20,
            "pass_limit": 3
        },
        "postprocess": {
            "method": "double_bridge_perturbation_then_2opt",
            "perturbations": 2,
            "strength": "small"
        },
        "selection": {
            "policy": "keep_best",
            "comparison": "tour_length",
            "deterministic_tie_break": "lexicographic"
        },
        "failure_replay": {
            "enabled": True,
            "archive_entries": 0,
            "compression": "none_yet",
            "use_replay": False
        },
        "robustness_bias": {
            "avoid_overfitting": True,
            "favor_generalization": True,
            "symmetric_treatment": True
        }
    }
