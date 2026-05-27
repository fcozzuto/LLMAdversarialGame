def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "objective": "constrained_tsp",
        "style": "interpretable_robust_heuristic",
        "properties": {
            "deterministic": True,
            "no_replay_archive": True,
            "complexity": "low",
            "transfer_priority": "held_out_tsplib_and_synthetic",
        },
        "components": {
            "construction": {
                "method": "nearest_neighbor_with_feasibility_filter",
                "tie_break": "min_delta_then_lowest_index",
                "seed_rule": "fixed_start_by_canonical_index",
            },
            "repair": {
                "method": "2-opt_local_improvement",
                "scope": "feasible_edges_only",
                "acceptance": "strict_improvement",
            },
            "compression": {
                "method": "failure_replay_compression",
                "behavior": "extract_common_failure_patterns_and_generalize",
                "archive_entries": [],
                "fallback": "generic_feasibility_safe_moves",
            },
            "candidate_selection": {
                "method": "greedy_beam",
                "beam_width": 3,
                "prune_rule": "dominance_and_infeasibility",
            },
        },
        "constraints": {
            "enforce_feasibility_at_each_step": True,
            "soften_only_when_dead_end": True,
            "dead_end_resolution": "minimal_violation_then_repair",
        },
        "evaluation": {
            "primary": "tour_length",
            "secondary": "constraint_violations",
            "tertiary": "repair_count",
        },
    }
