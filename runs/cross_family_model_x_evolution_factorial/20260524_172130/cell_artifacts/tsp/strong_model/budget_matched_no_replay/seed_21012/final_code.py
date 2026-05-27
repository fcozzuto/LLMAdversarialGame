def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "version": 1,
        "strategy": "candidate_1",
        "objective": "constrained_tsp",
        "priorities": [
            "feasibility_first",
            "cost_minimization",
            "stable_transfer",
        ],
        "components": {
            "construction": {
                "method": "nearest_neighbor_seeded",
                "seed_rule": "minimum_sum_distance",
                "tie_break": "lowest_index",
                "candidate_pool": 8,
            },
            "budget_matching": {
                "enabled": True,
                "mode": "soft_penalty",
                "penalty_weight": 1.0,
                "budget_slack": 0.02,
                "adjustment_rule": "trim_long_edges_first",
            },
            "improvement": {
                "enabled": True,
                "passes": 2,
                "operators": [
                    "2-opt",
                    "swap",
                ],
                "acceptance": "strict_improvement",
            },
            "robustness": {
                "metric": "normalized_cost",
                "distance_scaling": "instance_median",
                "outlier_handling": "cap_top_percentile",
                "cap_percentile": 95,
            },
        },
        "constraints": {
            "no_replay": True,
            "no_memory": True,
            "deterministic": True,
            "interpretable": True,
            "complexity": "low",
        },
    }
