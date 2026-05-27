def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic TSP heuristic scaffold with constrained transfer considerations.",
        "strategy": {
            "phases": [
                {
                    "phase_id": "initial_feasibility_and_baseline",
                    "objective": "generate a feasible tour respecting basic constraints (node visitation, all nodes exactly once).",
                    "methods": [
                        {
                            "type": "greedy_constrained_neighbor",
                            "params": {
                                "start_node": 0,
                                "tie_breaker": "lowest_index",
                                "constraint_checks": ["capacity", "precedence"],
                                "fallback": "nearest_neighbor",
                                "random_seed": 42  # deterministic
                            }
                        }
                    ],
                    "outputs": ["feasible_tour", "feasibility_flags"]
                },
                {
                    "phase_id": "constraint_violation_revision",
                    "objective": "repair minor constraint violations while preserving feasibility.",
                    "methods": [
                        {
                            "type": "local_repair",
                            "params": {
                                "repair_moves": ["2-opt_step", "swap_adjacent"],
                                "max_iterations": 100,
                                "policy": "accept_improvement_only"
                            }
                        }
                    ],
                    "outputs": ["repaired_tour", "violation_report"]
                },
                {
                    "phase_id": "transfer_insight_and_transferable_robustness",
                    "objective": "evaluate robustness across held-out TSPLIB-like instances and synthetic transfers.",
                    "methods": [
                        {
                            "type": "transfer_evaluation",
                            "params": {
                                "held_out_set": ["pcb3038", "rat783", "pr105"],
                                "synthetic_transfers": [
                                    {"name": "synthetic_env_01", "perturbation": "node_order_shuffle", "severity": 0.05},
                                    {"name": "synthetic_env_02", "perturbation": "distance_noise", "severity": 0.10}
                                ],
                                "metrics": ["tour_length", "feasibility", "computation_time"],
                                "seed": 42
                            }
                        }
                    ],
                    "outputs": ["transfer_performance", "robustness_profile"]
                }
            ],
            "selection": {
                "criterion": "balanced_performance",
                "weights": {
                    "feasibility": 0.25,
                    "tour_length": 0.35,
                    "robustness": 0.30,
                    "computation_time": 0.10
                }
            },
            "parameters": {
                "random_seed": 42,
                "verbosity": 0,
                "max_tours": 1,
                "max_runtime_seconds": 60
            }
        },
        "design_principles": [
            "deterministic_reproducibility",
            "interpretability",
            "robust_transfer_performance",
            "constrained_feasibility",
            "light_weight_scaffold"
        ],
        "notes": "This scaffold focuses on a deterministic, interpretable constrained TSP heuristic with phased evaluation including hold-out TSPLIB-like instances and synthetic transfers. No external archives are assumed; the failure_replay mechanism is prepared via deterministic seeds and fixed policy decisions."}
