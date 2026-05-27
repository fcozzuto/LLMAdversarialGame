def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP with budget_matched_no_replay technique.
    # This scaffold favors robust evaluation on held-out TSPLIB and synthetic transfer performance
    # while remaining interpretable and not overly complex.
    return {
        "name": "budget_matched_no_replay_scaffold",
        "version": 1,
        "description": "Deterministic, interpretable constrained TSP heuristic scaffold using budget matching without replay memory.",
        "technique": "budget_matched_no_replay",
        "properties": {
            "seed": 42,
            "random_state": 42,
            "budget_policy": {
                "type": "fixed_fraction",
                "fraction_of_cost": 0.75,
                "adjustment": "none"  # no dynamic budget adjustment during search
            },
            "constraining_constraints": {
                "time_limit_seconds": 0,    # no external time constraint (deterministic)
                "node_visit_limit": "unbounded"  # allow full exploration within deterministic rules
            },
            "tour_generation": {
                "initial_heuristic": "greedy_constrained",
                "neighbors": "2-opt_admissible",
                "local_search": "swap_and_relocate",
                "max_steps": 500
            },
            "cost_model": {
                "edge_cost": "euclidean",        # deterministic, reproducible on TSPLIB-like data
                "penalties": "on_violations",
                "penalty_factor": 1.0
            },
            "robustness_focus": {
                "held_out_evaluation": True,
                "synthetic_transfer": True,
                "training_bias_mitigation": True
            },
            "data_handling": {
                "datasets": [
                    "tsplib_heldout",
                    "synthetic_transfer"
                ],
                "split_strategy": "fixed_seed_split",
                "shuffle": False
            },
            "interpretability": {
                "algorithmic_steps": [
                    "build_initial_constrained_tour",
                    "apply_budget_bound",
                    "perform_local_search",
                    "validate_constraints",
                    "return_final_tour"
                ],
                "explanation_format": "human_readable",
                "determinism": True
            },
            "outputs": {
                "tour": None,  # to be filled by the caller with a list of node indices
                "cost": None,  # computed cost of the tour
                "status": "not_executed",
                "log": []
            }
        }
    }
