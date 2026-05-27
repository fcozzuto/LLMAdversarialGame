def build_heuristic():
    return {
        "name": "robust_insertion_2opt",
        "technique": "single_shot",
        "candidate": 1,
        "memory": {
            "prior_candidates": False,
            "replay_memory": False,
            "failure_memory": False,
            "compression": False,
        },
        "objectives": {
            "primary": "tour_length",
            "secondary": "robust_generalization",
        },
        "construction": {
            "seed_rule": "farthest_pair",
            "insertion_rule": "best_insertion",
            "tie_break": "deterministic_lexicographic",
        },
        "improvement": {
            "local_search": ["2-opt", "node_reinsertion"],
            "acceptance": "strict_improvement",
            "max_passes": 3,
        },
        "robustness": {
            "favor_metric": "euclidean_or_metric_tsp",
            "scale_invariant": True,
            "prefer_simple_structure": True,
            "avoid_instance_specific_tuning": True,
        },
        "transfer_bias": {
            "heldout_tsplib": "strong",
            "synthetic": "strong",
            "overfit_risk": "low",
        },
        "interpretability": {
            "level": "high",
            "notes": [
                "Start from a stable geometric seed.",
                "Insert nodes by minimum tour increase.",
                "Apply a small number of deterministic local-search passes.",
            ],
        },
    }
