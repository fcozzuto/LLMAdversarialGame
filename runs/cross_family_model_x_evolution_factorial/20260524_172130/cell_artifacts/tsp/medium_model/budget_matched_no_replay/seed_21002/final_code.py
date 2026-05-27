def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP using budgeting strategy
    # Budget-matched, no replay or memory components, simple transferable design.

    heuristic = {
        "name": "budget_matched_no_replay",
        "type": "approximate_constrained_tsp",
        "budget_policy": {
            "total_budget": 1000,        # general budget units for tour construction
            "per_step_budget": 20,       # budget allocated per decision step
            "budget_match": True,        # ensure budget aligns with problem scale
            "scaling": "linear",          # simple linear scaling with problem size
        },
        "construction_strategy": {
            "phase_order": ["seed_selection", "budgeted_extension", "local_improvement"],
            "seed_selection": {
                "strategy": "deterministic_nearest_neighbor",
                "start_node": "min_id",        # deterministic seed
                "constraints": {
                    "must_visit_in_order": False,
                    "fixed_start_node": 0
                }
            },
            "budgeted_extension": {
                "method": "greedy_with_budget",
                "cost_function": "edge_length",
                "restriction": "must_respect_capacity_and_time_windows",
                "iterations": 50,
                "tiebreaker": "lowest_id"
            },
            "local_improvement": {
                "method": "2opt_fix_constraints",
                "iterations": 20,
                "acceptance": "improve_or_equal",
                "constraints": {
                    "avoid_reversals_that_violate_constraints": True
                }
            }
        },
        "constraints_handling": {
            "types": ["time_windows", "vehicle_capacity"],
            "compatibility": {
                "time_windows": "loose",
                "capacity": "soft_bound_with_penalties"
            }
        },
        "scalability": {
            "problem_sizes_supported": [50, 100, 200, 500],
            "performance_hint": "good_transfer_to_synthetic_and_real_world_scenarios",
            "robustness": "moderate",
            "diagnostics": {
                "log_level": "warning",
                "metrics": ["route_length", "constraint_violations", "budget_usage"]
            }
        },
        "output_format": {
            "tour": "list_of_node_ids",
            "cost": "float",
            "status": "string",
            "metadata": {
                "seed_node": 0,
                "steps_taken": 0
            }
        }
    }
    return heuristic
