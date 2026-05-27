def build_heuristic():
    """
    Deterministic single-shot TSP heuristic scaffold for constrained TSPLIB and synthetic transfer evaluation.
    Returns a dictionary with interpretable, robust components without external imports.
    """
    heuristic = {
        # Basic meta-information
        "name": "constrained_tsp_heuristic_scaffold",
        "version": "1.0",
        "description": "Deterministic, interpretable single-shot heuristic scaffold for constrained TSP. Emphasizes robust performance on TSPLIB and synthetic transfers.",
        "seed": 42,

        # Problem handling
        "problem": {
            "type": "constrained_tsp",
            "constraints": [
                "must_visit_all_cities",
                "budget_or_capacity_constraint",
                "time_window_constraint_if_present",
            ],
            "distance_metric": "euclidean",
        },

        # Heuristic components (interpretable, deterministic)
        "components": {
            # 1) Preparatory scaling: normalize coordinates deterministically by min-max
            "normalization": {
                "method": "min_max_scale",
                "params": {
                    "scale_range": [0.0, 1.0],
                    "axis": "city_coordinates",
                },
            },
            # 2) Simple greedy seed path based on nearest neighbor with tie-breaking by index
            "seed_path": {
                "method": "nearest_neighbor",
                "params": {
                    "start_city_index": 0,  # deterministic starting city
                    "tie_break": "lowest_index",
                    "distance": "euclidean",
                },
            },
            # 3) Local improvement using 2-opt style passes with deterministic order
            "local_improvement": {
                "method": "2_opt",
                "params": {
                    "passes": 2,
                    "swap_order": ["segment_endpoints", "middle_pairs"],
                    "acceptance": "improvement_only",
                },
            },
            # 4) Constraint check and correction: simple fix to satisfy constraints without deep search
            "constraint_fix": {
                "method": "sanity_fix",
                "params": {
                    "strategy": "insert_unvisited_city_at_end",
                    "max_iterations": 10,
                },
            },
            # 5) Transfer robustness: deterministic fallback to synthetic transfer-safe permutation
            "transfer_fallback": {
                "method": "synthetic_transfer_permutation",
                "params": {
                    "seed": 42,
                    "scramble": False,
                    "preserve_structure": True,
                },
            },
        },

        # Scoring and evaluation (transparent, deterministic)
        "evaluation": {
            "objective": "minimize_total_distance",
            "constraints_enforced": True,
            "scoring": {
                "primary": "distance",
                "secondary": ["visits_count_diff", "constraint_violations"],
            },
            "robustness_estimation": {
                "method": "deterministic_analysis",
                "params": {
                    "test_sets": [
                        "tsplib_robust_holdout",
                        "synthetic_transfer_set",
                    ],
                    "thresholds": {
                        "distance_penalty": 1.0,
                        "violation_penalty": 100.0,
                    },
                },
            },
        },

        # Output format
        "output": {
            "format": "sequence_of_city_indices",
            "fields": ["order", "city_index", "cumulative_distance"],
        },
    }

    return heuristic
