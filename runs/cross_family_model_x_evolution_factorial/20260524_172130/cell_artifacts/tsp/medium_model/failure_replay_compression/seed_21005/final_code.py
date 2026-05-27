def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # This scaffold emphasizes robustness over training-only performance,
    # supports held-out TSPLIB-like instances, and remains interpretable.

    scaffold = {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1.0,
        "description": (
            "A deterministic scaffold for a constrained TSP heuristic using "
            "a simple, interpretable approach with failure-replay_compression "
            "style notes. Designed for robustness across held-out TSPLIB-like "
            "instances and synthetic transfer benchmarks."
        ),
        "technique": "failure_replay_compression",
        "variant": "Candidate_1",
        "failure_replay_archive": {
            "entries": [],
            "notes": "No replay archive entries are available yet."
        },
        "problem_space": {
            "type": "constrained_tsp",
            "constraints": [
                "hard_constraints",
                "budget_or_time_constraint",
                "precedence_or_tlexible_constraints"
            ],
            "instance_source": ["tsplib_like", "synthetic_transfer"],
            "goal": "minimize_path_cost_with_constraints",
        },
        "heuristic_components": {
            "initialization": {
                "method": "greedy_feasible_seed",
                "seed_strategy": "nearest_feasible_start",
                "deterministic": True
            },
            "construction": {
                "step_order": "progressive_insertion",
                "insertion_rule": "min_cost_increment_with_constraint_check",
                "neighborhood": "local_neighborhood",
                "lookahead": 1
            },
            "repair": {
                "enabled": True,
                "method": "local_swaps_that_preserve_constraints",
                "limit": 100,
                "deterministic": True
            },
            "termination": {
                "criterion": "no_improvement_epochs",
                "max_epochs": 10,
                "tol": 1e-6
            }
        },
        "transfer_and_robustness": {
            "transfer_focus": ["held_out_tsplib_like", "synthetic_transfer"],
            "robustness_measures": [
                "cost_variation_across_instances",
                "constraint_violation_rate",
                "solution_stability_under_small_changes"
            ],
            "evaluation_protocol": {
                "train_test_split": "not_used_for_training",
                "held_out_evaluation": True,
                "repeatability": "deterministic_runs_only"
            }
        },
        "interpretability": {
            "explanation": "sequence_of_insertion_and_repair_steps",
            "traceability": "each_decision_logged_with_cost_and_constraint_status",
            "simplification": "option_to_export_subroutes_and_costs"
        },
        "configuration": {
            "random_seed": 42,
            "logging": {
                "level": "warning",
                "handlers": ["console"]
            },
            "limits": {
                "max_runtime_seconds": 5,
                "max_nodes_evaluated": 1000
            }
        }
    }

    return scaffold
