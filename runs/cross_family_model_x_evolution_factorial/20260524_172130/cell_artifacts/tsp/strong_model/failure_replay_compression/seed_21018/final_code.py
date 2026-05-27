def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "objective": "minimize_tour_length",
        "design_goals": [
            "robust_transfer",
            "interpretable",
            "deterministic",
            "simple"
        ],
        "construction": {
            "method": "nearest_insertion",
            "seed_rule": "farthest_pair",
            "tie_break": "lowest_index",
            "start_strategy": "best_of_three_fixed_candidates"
        },
        "local_search": {
            "method": "2-opt",
            "acceptance": "strict_improvement",
            "scan_order": "deterministic",
            "restart": False,
            "max_passes": 8
        },
        "repair": {
            "method": "segment_relink",
            "trigger": "when_stagnant",
            "compression": "remove_redundant_improvements",
            "limit": 2
        },
        "candidate_pruning": {
            "use_nearest_neighbors": True,
            "k": 20,
            "prune_long_edges": True,
            "edge_threshold_rule": "relative_to_median_incident_length"
        },
        "fallbacks": {
            "if_degenerate": "greedy_2opt_only",
            "if_small_n": "exhaustive_start_selection"
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": "improvement_stability",
            "tertiary": "runtime"
        },
        "notes": [
            "Replay-free compression: use only compact failure-derived rules, no archive dependence.",
            "Designed to generalize across TSPLIB-like and synthetic Euclidean instances."
        ]
    }
