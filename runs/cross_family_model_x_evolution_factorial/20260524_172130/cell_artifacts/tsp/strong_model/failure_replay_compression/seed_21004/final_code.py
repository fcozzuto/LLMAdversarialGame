def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "mode": "constrained_tsp_heuristic_scaffold",
        "goals": {
            "primary": "robust held-out TSPLIB and synthetic transfer performance",
            "secondary": "interpretability",
            "tertiary": "avoid overfitting to training instances",
        },
        "strategy": {
            "construction": [
                "start from a geometry-aware seed tour",
                "repair using local edge exchanges under constraints",
                "compress repeated failure patterns into reusable move priorities",
            ],
            "local_search": [
                "2-opt",
                "3-opt-lite",
                "node relocation",
            ],
            "tie_breaking": "deterministic",
            "restart_policy": "none",
        },
        "failure_replay_compression": {
            "enabled": True,
            "archive_available": False,
            "when_no_archive": "use conservative generic penalties and safe improvements only",
            "compressed_failures": [
                "crossing-heavy moves",
                "long detours near boundary nodes",
                "constraint-violating shortcuts",
            ],
            "priority_adjustments": [
                "prefer edge removals that reduce crossings first",
                "prefer short-to-short replacements when distances are ambiguous",
                "avoid repeating rejected move signatures",
            ],
        },
        "scoring": {
            "objective": "tour_length",
            "constraint_penalty": "large",
            "move_cost": "delta_length_plus_penalty",
            "robustness_bias": "mild",
        },
        "parameters": {
            "candidate_edge_limit": 24,
            "relocation_limit": 16,
            "max_passes": 4,
            "accept_non_improving": False,
        },
        "representation": {
            "tour_format": "permutation",
            "edge_cache": True,
            "invariant_checks": [
                "valid permutation",
                "constraint feasibility",
                "deterministic ordering",
            ],
        },
        "notes": [
            "Designed to transfer well across Euclidean-like and mixed TSPLIB instances.",
            "Keeps the heuristic interpretable and compact.",
        ],
    }
