def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "archive_available": False,
        "goal": "robust_transfer",
        "target": "constrained_tsp",
        "interpretability": "high",
        "complexity": "low",
        "strategy": {
            "type": "multi_start_replay",
            "selection": "deterministic",
            "replay_policy": "best_seen_then_diverse",
            "fallback": "greedy_nearest_insertion",
        },
        "construction": {
            "initializer": "farthest_pair_seed",
            "insertion": "cheapest_feasible_insertion",
            "candidate_list_size": 10,
            "tie_break": "lexicographic",
        },
        "improvement": {
            "local_search": ["2-opt", "relocate"],
            "acceptance": "strict_improvement",
            "restart_budget": 8,
        },
        "constraints": {
            "enforce_during_construction": True,
            "repair_infeasible": True,
            "repair_method": "minimal_adjustment",
        },
        "transfer_bias": {
            "prefer_geometric": True,
            "scale_invariant": True,
            "robust_to_noise": True,
        },
        "randomness": {
            "enabled": True,
            "seed_policy": "fixed_sequence",
            "replay": "deterministic_permutation",
        },
    }
