def build_heuristic():
    # Deterministic TSP heuristic scaffold: budget_matched_no_replay
    # Returns a constrained TSP heuristic specification with interpretable components.
    scaffold = {
        "name": "budget_matched_no_replay",
        "technique": "adaptive_constrained_tsp",
        "description": (
            "Deterministic heuristic scaffold using budget-matched traversal with simple "
            "greedy augmentation and feasibility checks. No replay/failure memory. "
            "Aimed at robust performance on TSPLIB-like and synthetic transfer instances."
        ),
        "parameters": {
            # Budget matching: total allowed tour length budget
            "budget_fraction_of_optimal_guess": 0.95,  # heuristic assumes near-optimal total length
            "initial_seed": 1,  # deterministic seed
            "max_iterations": 1000,
            "step_size": 1,
            "verbosity": 0
        },
        "feasibility_checks": {
            "type": "degree_constraint",
            "max_degree": 2,
            "subtour_elimination": {
                "enabled": True,
                "method": "lazy_pruning"  # lightweight feasibility checks
            }
        },
        "construction_rule": {
            "method": "greedy_nearest_neighbor_with_feasibility",
            "start_node": "deterministic_min_id",
            "neighbor_selection": {
                "strategy": "closest_feasible",
                "tie_breaker": "lowest_id"
            }
        },
        "tour_completion": {
            "closing_edge": {
                "strategy": "connect_to_start_if_feasible",
                "fallback": "connect_to_nearest_start"
            },
            "local_improvements": {
                "enabled": False
            }
        },
        "robustness_considerations": {
            "tsplib_transfer_focus": True,
            "synthetic_transfer_focus": True,
            "instance_balance": {
                "training_vs_testing_ratio": 0.0  # not using replay; fixed evaluation
            }
        },
        "outputs": {
            "tour_representation": "list_of_node_ids_in_order",
            "quality_metrics": {
                "tour_length": None,
                "feasibility": True
            }
        }
    }
    return scaffold
