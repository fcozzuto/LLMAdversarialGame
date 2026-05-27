def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic.
    # Design goals:
    # - Robust across held-out TSPLIB and synthetic transfer instances
    # - Simple, interpretable, not overly complex
    # - No external imports; self-contained configuration

    scaffold = {
        # Problem characterization and constraints
        "problem": {
            "name": "constrained_tsp_heuristic",
            "constraints": [
                "must_visit_all_cities_once",
                "city_visit_order respects_precedence_constraints",
                "requires_subtour_elimination",
                "edge_costs_assume_symmetric_or_asymmetric_flag",
            ],
            "instances": {
                "held_out_tsplib": True,
                "synthetic_transfer": True
            }
        },

        # Heuristic strategy outline
        "strategy": {
            # Stage 1: Initialization
            "initialization": {
                "method": "greedy_nearest_neighbor_with_constraints",
                "seed": 1337,  # deterministic seed
                "start_city_choice": "lowest_index",
                "feasible_next_selection": True
            },
            # Stage 2: Repair and improvement
            "repair": {
                "method": "local_subtour_elimination_and_feasibility_fix",
                "max_iterations": 50,
                "tolerance": 1e-6
            },
            "improvement": {
                "methods": [
                    "2_opt_with_constraints",
                    "or_opt_with_constraints"
                ],
                "max_subpath_length": 3,
                "iteration_limit": 200
            }
        },

        # Constraint handling
        "constraints": {
            "precedence": {
                "enabled": True,
                "ruleset": "predefined_flags",  # placeholder for deterministic rules
                "compatibility_check": True
            },
            "subtour_elimination": {
                "enabled": True,
                "cutting_plane_style": "dynamic",
                "guard_distance": 0.0
            }
        },

        # Scoring and decision internal representation
        "score":

        {
            "objective": "minimize_total_distance",
            "edge_cost_metric": "euclidean" if "symmetric" else "asymmetric",
            "penalties": {
                "violation_of_precedence": 1000.0,
                "repeat_visit_penalty": 500.0,
                "subtour_penalty": 700.0
            },
            "normalization": {
                "normalize_by": "route_length"
            }
        },

        # Data flow and interfaces (deterministic)
        "interfaces": {
            "input": {
                "cities": "list_of_city_objects_with_coords_and_constraints",
                "distance_matrix": "optional; if absent, compute via coords",
                "precedence_matrix": "optional; enforces order constraints"
            },
            "output": {
                "tour": "ordered_list_of_city_indices",
                "cost": "float_total_cost",
                "feasibility": "boolean"
            }
        },

        # Robustness and reproducibility
        "robustness": {
            "deterministic_seed": 1337,
            "fallbacks": [
                "if_no_feasible_solution, return_empty_tour_with_cost_inf",
                "logistic_reference_state_for_debugging"
            ],
            "monitoring": {
                "metrics": ["feasibility_rate", "average_tour_cost", "subtour_count"],
                "aggregation": "per_instance"
            }
        },

        # Extensibility hints (not too complex)
        "extensibility": {
            "swap_strategy": "simple_pair_swap_only_if_improves",
            "parallelization": False
        }
    }

    return scaffold
