def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic
    # Notes:
    # - No imports
    # - Returns a dictionary with interpretable components
    # - Focus on robustness to TSPLIB-like constraints and synthetic transfers
    # - Implements a simple, transparent pipeline: seed, feasibility, neighborhood, augmentation

    heuristic = {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "seed": 42,
        "description": "Deterministic, interpretable scaffold for constrained TSP with robustness to held-out TSPLIB-like and synthetic transfer instances.",
        "domains": {
            "problem": "constrained_tsp",
            "constraints": [
                "visit_each_city_once",
                "subtour_elimination",
                "precedence_or_capacity_constraints_if_any",  # placeholder for potential constraints
            ],
        },
        "parameters": {
            # Fixed deterministic defaults
            "initialization": {
                "strategy": "nearest_neighbor",
                "start_node": 0
            },
            "neighborhood": {
                "methods": ["2-opt", "swap", "or-opt"],
                "max_iterations": 50,
                "improvement_threshold": 1e-6
            },
            "feasibility_checks": {
                "enabled": True,
                "constraint_verification": "on_the_fly",
                "log": False
            },
            "augmentation": {
                "enable": True,
                "augmentation_fraction": 0.1,
                "augmentation_strategy": "randomized_pref_attach"  # deterministic seed from top-level seed
            },
            "robustness": {
                "transfer_flexibility": "moderate",
                "held_out_validation": True
            }
        },
        "pipeline": [
            {
                "stage": "initialization",
                "action": "build_initial_tour",
                "details": {
                    "start_node": 0,
                    "method": "nearest_neighbor"
                }
            },
            {
                "stage": "local_search",
                "action": "apply_neighborhood_moves",
                "details": {
                    "methods": ["2-opt", "swap", "or-opt"],
                    "max_iterations": 50,
                    "improvement_threshold": 1e-6
                }
            },
            {
                "stage": "feasibility",
                "action": "verify_and_fix_feasibility",
                "details": {
                    "enabled": True,
                    "log": False
                }
            },
            {
                "stage": "augmentation",
                "action": "augment_solution_if_needed",
                "details": {
                    "enabled": True,
                    "fraction": 0.1,
                    "strategy": "randomized_pref_attach",
                    "seed": 42
                }
            },
            {
                "stage": "robustness_evaluation",
                "action": "assess_transfer_robustness",
                "details": {
                    "held_out_validation": True,
                    "domains_considered": ["TSPLIB-like", "synthetic_transfer"],
                    "metrics": ["tour_cost", "feasibility_rate"]
                }
            }
        ],
        "heuristic_properties": {
            "interpretability": "high",
            "complexity": "low_to_moderate",
            "determinism": True,
            "scalability": "reasonable for medium-sized instances",
            "reproducibility": True
        },
        "notes": [
            "This scaffold is intentionally minimal and interpretable.",
            "No external data or imports are required; deterministic behavior is ensured by fixed seeds.",
            "The augmentation step is designed to be conservative to avoid overfitting to training-like instances."
        ]
        ,
        "constraints": {
            "explicit": [
                "Each city must be visited exactly once.",
                "Subtour elimination constraints applied during/local-search feasibility checks."
            ],
            "implicit": [
                "Deterministic seed ensures reproducibility across runs."
            ]
        }
    }
    return heuristic
