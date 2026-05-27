def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP (single_shot, Candidate 1)
    # This dictionary encodes a simple, interpretable blueprint that can be used
    # to construct a heuristic without external dependencies or imports.
    return {
        "name": "single_shot_constrained_tsp_heuristic",
        "version": "1.0",
        "description": "Robust, interpretable one-shot heuristic scaffold for constrained TSP with TSPLIB and synthetic transfer focus.",
        "assumptions": {
            "problem_class": "constrained_tsp",
            "nodes": "unknown_at_runtime",
            "edges": "fully_connected_with_costs",
            "constraints": {
                "time_window": False,
                "capacity": False,
                "precedence": False
            },
            "seed_determinism": True
        },
        "input_shape": {
            "nodes": "int",
            "constraints": {
                "travel_budget": "optional_float_or_none",
                "required_nodes": "optional_set_or_none"
            }
        },
        "heuristic_components": {
            "initial_construction": {
                "type": "greedy_path_build",
                "strategy": "nearest_neighbor_with_constraints",
                "start_node": "deterministic_min_index",
                "tie_breaker": "lowest_node_index",
            },
            "feasibility_adjustment": {
                "type": "local_improvement",
                "method": "2-opt",
                "allowed_reversals": True,
                "constraint_checks": "strict",
            },
            "constraint_handling": {
                "approach": "soft_to_hard",
                "penalty_function": "quadratic",
                "penalty_coefficient": 1.0,
                "budget_guard": "global_travel_budget_if_given"
            },
            "termination_criteria": {
                "iterations": 100,
                "improvement_threshold": 1e-6,
                "stagnation_checks": 5
            }
        },
        "output": {
            "tour": "list_of_node_indices_in_order",
            "cost": "float_total_cost",
            "feasible": "bool",
            "diagnostics": {
                "steps": "int",
                "improvements": "int",
                "runtime_ms": "float"
            }
        },
        "robustness_features": {
            "tsplib_compatibility": True,
            "synthetic_transfer_ready": True,
            "memoization": False,
            "memory_usage": "low",
            "determinism": True
        }
    }
