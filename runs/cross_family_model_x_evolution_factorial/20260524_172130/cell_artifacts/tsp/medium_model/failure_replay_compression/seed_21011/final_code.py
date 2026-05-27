def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for a constrained TSP heuristic with emphasis on robust held-out TSPLIB and synthetic transfer performance.",
        "parameters": {
            "seed": 42,
            "max_iterations": 1000,
            "perturbation_fraction": 0.2,
            "convergence_tolerance": 1e-6,
            "stop_when_improvement_stalls": True
        },
        "techniques": [
            {
                "name": "initial_solution",
                "description": "Generate a feasible baseline tour respecting constraints using a deterministic greedy construction.",
                "method": "greedy_constrained_build",
                "constraints": [
                    "must_visit_once_per_node",
                    "respect_capacity_limits",
                    "respect_tour_time_windows_if_present"
                ],
                "seed_usage": "seed"
            }
        ],
        "optimization_loop": {
            "type": "iterative_improvement",
            "methods": [
                {
                    "name": "2opt_with_constraints",
                    "description": "Apply 2-opt style reversals that preserve feasibility with respect to constraints.",
                    "feasibility_check": "validate_tour_feasibility",
                    "objective": "minimize_cost"
                },
                {
                    "name": "swap_and_relocate_with_constraints",
                    "description": "Swap nodes or relocate subpaths while maintaining feasibility.",
                    "feasibility_check": "validate_tour_feasibility",
                    "objective": "minimize_cost"
                }
            ],
            "stopping_criteria": {
                "no_improvement_epochs": 20,
                "convergence_tolerance": "convergence_tolerance in parameters"
            },
            "failure_replay": {
                "technique": "failure_replay_compression",
                "description": "Deterministic replay compression to reuse prior failure patterns; no replay archive entries yet.",
                "archive_used": False,
                "notes": "No replay data available; scaffold remains deterministic."
            }
        },
        "transfer_learning_considerations": {
            "robustness_focus": [
                "evaluate_on_held_out_TSPLIB",
                "include_synthetic_transfers_with_varied_constraints",
                "avoid_overfitting_to_training_instances"
            ],
            "transfer_modes": [
                "same_constraint_family",
                "vary_vehicle_capacities",
                "vary_time_windows"
            ],
            "evaluation_metrics": [
                "tour_cost",
                "feasibility_rate",
                "runtime",
                "solution_stability_across_runs"
            ]
        },
        "outputs": {
            "tour": None,
            "cost": None,
            "status": "uninitialized"
        }
    }
