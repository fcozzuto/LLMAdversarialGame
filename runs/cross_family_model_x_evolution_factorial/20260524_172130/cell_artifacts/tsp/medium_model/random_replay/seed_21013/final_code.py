def build_heuristic():
    return {
        "name": "deterministic_constrained_tsp_heuristic",
        "version": "1.0",
        "description": "A robust, interpretable constrained TSP heuristic scaffold using deterministic components. Emphasizes held-out TSPLIB and synthetic transfer performance.",
        "technique": "random_replay",
        "strategy": {
            "step_order": ["build_feasible_baseline", "apply_constraint_reduction", "perform_greedy_extend", "local_improvement"],
            "seed_consistency": True,
            "replay_sources": {
                "archive_available": False,
                "fallback": "deterministic_stub",
            }
        },
        "problem_scope": {
            "constraints": [
                "vehicle_capacity",
                "route_length_upper_bound",
                "precedence_constraints",
                "time_windows_optional"
            ],
            "instances_considered": [
                "TSPLIB_constrained_like",
                "synthetic_transferable",
                "small_to_medium_scale_for_debug"
            ],
            "robustness_targets": [
                "holdout_tsplib",
                "synthetic_transfer_performance",
                "baseline_training_agreement"
            ]
        },
        "heuristic_components": [
            {
                "name": "feasible_baseline_builder",
                "description": "Construct an initial feasible tour respecting hard constraints using a deterministic heuristic (e.g., nearest-feasible with constraint checks).",
                "determinism_key": "baseline_builder_v1"
            },
            {
                "name": "constraint_reduction",
                "description": "If constraints cause infeasibility, locally reduce tight constraints in a controlled, deterministic manner to regain feasibility without breaking interpretability.",
                "determinism_key": "constraint_reduction_v1"
            },
            {
                "name": "greedy_extend",
                "description": "Extend tour greedily by selecting the best feasible city-to-city insertion under current constraints using a simple scoring function.",
                "determinism_key": "greedy_extend_v1"
            },
            {
                "name": "local_improvement",
                "description": "Apply small, deterministic local improvements (2-opt style) within feasibility bounds to improve objective while preserving constraints.",
                "determinism_key": "local_improvement_v1"
            }
        ],
        "scoring_and_objectives": {
            "objective": "minimize_cost_within_constraints",
            "cost_components": ["travel_distance", "constraint_violation_penalty"],
            "penalties": {
                "soft_violations": 0.0,
                "hard_violations": 1e9
            }
            ,
            "normalization": "per_instance"
        },
        "parameters": {
            "search_budget_nodes": 5000,
            "greedy_beam_width": 1,
            "local_improvement_limit": 100,
            "tie_breaker": "lexicographic"
        },
        "output_spec": {
            "tour": "list of location indices in visit order",
            "feasible": "bool indicating constraint satisfaction",
            "quality_metrics": {
                "distance": "float",
                "constraint_violation_score": "float"
            }
        },
        "notes": [
            "Deterministic seed is embedded in all components to ensure reproducibility.",
            "No external archives used; behavior is predictable across runs.",
            "The scaffold remains interpretable to allow inspection of each stage."
        ]
    }
