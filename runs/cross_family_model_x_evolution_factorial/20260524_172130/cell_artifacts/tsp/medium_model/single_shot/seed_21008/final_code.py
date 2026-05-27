def build_heuristic():
    return {
        "name": "constrained_tsp_scalar_heuristic",
        "version": "1.0",
        "description": "Deterministic single-shot scaffold for a constrained TSP heuristic using a robust yet interpretable strategy.",
        "strategy": "greedy_constrained_example",
        "parameters": {
            "seed": 42,
            "city_penalty_factor": 1.0,        # penalty weight for violating constraints
            "sequence_cost_weight": 1.0,       # weight for edge cost in sequence
            "constraint_tolerance": 0.0,        # tolerance for constraint violations (0 means strict)
            "max_neighborhood": 2,               # local search neighborhood radius (interpretable)
            "early_stop_improvement": 1e-6,      # stop if no improvement beyond this delta
            "time_budget_seconds": 0,            # placeholder for deterministic environments (no time-based variation)
            "max_iterations": 1000
        },
        "constraints": {
            "must_visit_all": True,
            "vehicle_capacity": None,            # None means simple visit-based constraint; can be specified per instance
            "time_windows": False,               # not using time windows in this scaffold
            "subtour_elimination": True
        },
        "initial_solution": {
            "method": "nearest_neighbor_with_constraints",
            "seed": 42
        },
        "scoring": {
            "edge_cost": "euclidean_distance",    # deterministic distance metric
            "constraint_violation_penalty": "linear",
            "balance": "cost_then_constraints"
        },
        "neighborhood_search": {
            "enabled": True,
            "method": "2-opt_limited",
            "delta_threshold": 1e-6,
            "max_swaps": 100
        },
        "transfer_assessment": {
            "robustness_focus": True,
            "holdout_sets": ["TSPLIB140", "TSPLIB199", "synthetic_transfer"],
            "metrics": ["relative_gap_to_optimal", "robustness_across_instances", "transfer_performance"],
            "statistical_summary": {
                "mean": True,
                "median": True,
                "std_dev": True
            }
        },
        "interpretability": {
            "description_trace": True,
            "decision_log_components": ["selected_edge_cost", "constraint_penalty", "heuristic_step_index"],
            "explainability_level": "moderate"
        },
        "determinism": {
            "seed_dependency": True,
            "pseudorandom_generator": "consistent_seed"
        },
        "notes": "This scaffold uses a single-shot greedy constrained approach with a simple local improvement step and deterministic scoring to ensure reproducibility and interpretability across conventional TSPLIB and synthetic transfer sets."}
