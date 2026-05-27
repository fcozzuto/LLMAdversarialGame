def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_single_shot",
        "version": "1.0",
        "description": "Deterministic single-shot constrained TSP heuristic scaffold with robust evaluation guidance.",
        "technique": "single_shot",
        "targets": {
            "constrained_objective": True,
            "feasibility_requirements": [
                "all_cities_visited_once",
                "subtour_elimination",
                "capacity_or_time_window_constraints_if_present"
            ],
        },
        "data_sources": {
            "held_out_tsplib": {
                "include": ["berlin52", "ch130", "k40_2", "pr76"],
                "exclude": [],
                "usage": "quality_estimation_and_fallback_baseline"
            },
            "synthetic_transfer": {
                "include": ["synthetic_clusters_A", "synthetic_clusters_B"],
                "usage": "transfer_performance_insight"
            }
        },
        "algorithm": {
            "type": "constructive_heuristic",
            "construction_order": ["nearest_neighbor_with_pruning", "insertion_with_constraints"],
            "pruning": {
                "enable": True,
                "method": "feasibility_check",
                "cost_adjustment": "simple_penalty",
                "threshold": 0.0
            },
            "insertion_rules": {
                "rule": "lowest_addition_cost_with_constraint_check",
                "tie_breaker": "lexicographic_city_id",
                "limit": 100  # safeguard for interpretability
            }
        },
        "parameters": {
            "seed": 1,
            "tour_initialization": "fixed_order",
            "neighborhood_size": 5,
            "max_runtime_seconds": 5,
            "constraint_tolerance": 1e-6
        },
        "evaluation": {
            "metrics": ["tour_length", "feasibility_rate", "subtour_count"],
            "benchmark": {
                "tsplib_instance_set": ["berlin52", "kroA100", "mona lisa"],
                "synthetic_set": ["synthetic_small", "synthetic_medium"]
            },
            "fallback_behavior": "return_best_feasible_found",
            "interpretability": True
        },
        "output": {
            "format": "dictionary",
            "entries": {
                "tour": "list_of_city_indices_in_order",
                "length": "float",
                "feasible": "bool",
                "status": "string_message"
            }
        },
        "notes": [
            "Deterministic: uses fixed seed and fixed ordering.",
            "Avoids heavy dependencies; no imports required.",
            "Designed as scaffold: easily extended with alternative constraint handling while preserving interpretability."
        ]
    }
