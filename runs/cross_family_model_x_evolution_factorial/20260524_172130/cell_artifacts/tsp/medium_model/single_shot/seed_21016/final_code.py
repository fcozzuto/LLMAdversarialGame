def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP using a single-shot, interpretable approach.
    # The dictionary encodes configuration, simple scoring, and deterministic parameters.
    return {
        "name": "single_shot_constrained_tsp_heuristic",
        "version": 1,
        "description": (
            "Deterministic, interpretable scaffold for a constrained TSP heuristic. "
            "Designed to be robust on TSPLIB-like and synthetic transfer instances without training."
        ),
        "technique": "single_shot",
        "domain": {
            "problem_type": "constrained_tsp",
            "constraints": {
                # Example high-level constraint definitions; kept explicit for interpretability.
                "start_node_fixed": False,
                "end_node_fixed": False,
                "budget": {
                    "type": "max_total_distance",
                    "value": None  # No global distance bound by default; can be set by user.
                },
                "visit_limits": {
                    "per_node": None,  # optional per-node visit limits
                    "total_visits": None  # optional total visits limit
                }
            },
            "distance_matrix": {
                "type": "symmetric_or_asymmetric",  # either, but deterministic path chosen
                "storage": "in_memory"  # no external I/O in the heuristic
            }
        },
        "strategy": {
            # Simple, deterministic scoring to build a tour in a greedy fashion with constraints.
            "initialization": {
                "method": "fixed_start_choice",
                "start_node": 0
            },
            "construction": {
                "method": "greedy_nearest_feasible",
                "feasibility": "check_capacity_and_release",
                "tie_breaker": "highest_minimum_remaining",
                "randomization": 0.0  # fully deterministic
            },
            "neighborhood": {
                "type": "one_pass_extension",
                "allowed_moves": ["insert", "swap_each_step"],
                "max_steps": 1000
            },
            "termination": {
                "criterion": "no_improvement_in_this_pass",
                "max_iterations": 1,
                "early_stop": True
            }
        },
        "parameters": {
            # Deterministic numeric settings to keep interpretability.
            "distance_weight": 1.0,
            "constraint_weight": 1.0,
            "priority_scheme": "lexicographic",
            "min_improvement": 0.0,
            "time_budget_seconds": 0.0,  # no wall-clock time, deterministic
            "normalize": False
        },
        "outputs": {
            "tour": None,  # deterministic tour will be filled by evaluator
            "cost": None,
            "statistics": {
                "steps_taken": 0,
                "feasible_checks": 0,
                "nodes_in_tour": 0,
                "terminate_reason": "not_run_yet"
            }
        },
        "robustness_and_transfer": {
            # Design choices to support TSPLIB and synthetic transfer without learning.
            "transfer_robustness": {
                "include_tsplib_like_variants": True,
                "synthetic_variants": True,
                "distance_scaling": "same_scale_for_all",
                "noise_resilience": False
            },
            "interpretability": {
                "monotone_scored": True,
                "explainable_decisions": True
            }
        },
        "notes": [
            "This scaffold is deterministic, readable, and does not depend on training data.",
            "Outputs are to be populated by an external evaluator; initial fields are placeholders.",
            "No external imports or randomness; suitable for straightforward integration."
        ]
    }
