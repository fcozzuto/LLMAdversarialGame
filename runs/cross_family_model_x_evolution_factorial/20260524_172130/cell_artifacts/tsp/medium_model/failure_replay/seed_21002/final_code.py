def build_heuristic():
    return {
        "name": "constrained_tsp_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for a constrained TSP heuristic with interpretable components and robust evaluation strategy.",
        "assumptions": {
            "instances": {
                "types": ["TSPLIB_surrogate", "synthetic_transferable"],
                "constraints": ["node_budget", "subtour_elimination", "time_window"],
            },
            "transfer_evaluation": {
                "focus": ["robust_held_out_performance", "generalization_across_instances"],
                "datasets": ["held_out_TSPLIB", "synthetic_transfers"],
            },
        },
        "heuristic_components": [
            {
                "name": "initial_solution",
                "description": "Construct a deterministic initial tour respecting simple constraints using a nearest-neighbor pass with fixed tie-breaking.",
                "method": "deterministic_nearest_neighbor",
                "parameters": {
                    "start_node_index": 0,
                    "tie_breaker": "lowest_index",
                    "steps": "visit_all_vertices"
                }
            },
            {
                "name": "constraint_enforcer",
                "description": "Apply immediate constraint checks and prune infeasible moves with minimal overhead.",
                "method": "prune_infeasible_moves",
                "parameters": {
                    "constraints": ["subtour_free", "budget_limits"]
                }
            },
            {
                "name": "local_improvement",
                "description": "Leave-one-out pairwise swaps and 2-opt with deterministic ordering to avoid randomness.",
                "method": "deterministic_2opt",
                "parameters": {
                    "iterations": 10,
                    "order": "increasing_index",
                    "acceptance_criteria": "improvement_only"
                }
            },
            {
                "name": "fallback_strategy",
                "description": "If constraints prevent full tour, produce a feasible partial tour with explicit budgeted refund or dummy penalties.",
                "method": "partial_solution_from_feasible_subtour",
                "parameters": {
                    "min_subtour_length": 4,
                    "penalty_for_missing_nodes": 1.0
                }
            },
            {
                "name": "transfer_evaluation",
                "description": "Ensure performance is evaluated on held-out TSPLIB and synthetic transfer instances with stable metrics.",
                "method": "evaluate_on_holdout",
                "parameters": {
                    "metrics": ["tour_cost", "feasibility_rate", "runtime"],
                    "datasets": ["held_out_tsplib", "synthetic_transfer"],
                    "repeat": 1
                }
            }
        ],
        "evaluation_protocol": {
            "setup": "deterministic_run",
            "repeatability": "single_run",
            "metrics": ["cost", "feasibility", "runtime"],
            "holdout_strategy": {
                "tsplib_fraction": 0.2,
                "synthetic_fraction": 0.3
            },
            "robustness_checks": ["edge_case_constraints", "dense_regions"]
        },
        "interpretability": {
            "loggable_components": ["initial_solution", "subtour_elimination", "local_improvement"],
            "explanation_points": [
                "cost_components",
                "constraint_violations",
                "improvement_steps"
            ]
        },
        "determinism": {
            "seed_control": {
                "enabled": True,
                "seed": 0
            },
            "random_sources": []
        }
    }
