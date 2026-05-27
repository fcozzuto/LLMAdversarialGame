def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP (budget_matched_no_replay)
    # Notes:
    # - No imports
    # - Interpretable, not overly complex
    # - Emphasizes robustness on held-out TSPLIB-like and synthetic transfer performance
    # - Uses a budget-matched, no-replay strategy (no memory of past failures or rehearsals)
    # - Returns a dictionary describing the scaffold components and parameters

    scaffold = {
        "name": "budget_matched_no_replay_constrained_tsp",
        "description": (
            "Deterministic TSP heuristic scaffold with simple, budget-aware construction "
            "and greedy extension under a side constraint model. Emphasizes robustness "
            "across held-out TSPLIB-like instances and synthetic transfers."
        ),
        "strategy": {
            "type": "greedy_budget_constrained",
            "budget_definition": {
                "budget_type": "path_cost",
                "budget_source": "computed_from_instance",
                "allowable_margin": 0.02  # 2% tolerance for budget matching
            },
            "initialization": {
                "start_node": "nearest_to_origin",  # deterministic: choose a fixed origin node index 0
                "origin_index": 0
            },
            "feasibility_check": {
                "constraint_model": "capacity_like",
                "capacity_limit": 0.9  # normalized capacity threshold for illustration
            },
            "extension_rule": {
                "method": "greedy_nearest_feasible",
                "tie_breaker": "lowest_incremental_cost",
                "visited_handling": "no_revisit",
                "step_limit": "n_dimensional_constant",  # placeholder to keep deterministic behavior
            }
        },
        "constrained_model": {
            "node_constraints": {
                "mandatory_nodes": [],      # list of node indices that must be visited (empty by default)
                "forbidden_nodes": [],      # list of node indices that must be avoided (empty by default)
                "node_priors": None           # optional per-node desirability, None means equal
            },
            "edge_constraints": {
                "forbidden_edges": [],        # e.g., (i, j) pairs
                "required_edges": []           # e.g., (i, j) pairs that must be included
            },
            "budget_handling": {
                "budget_type": "path_cost",
                "target_cost": "as_in_instance",  # placeholder to align with instance-derived budget
                "allowable_deviation": 0.02
            }
        },
        "transfer_robustness": {
            "held_out_evaluation": True,
            "synthetic_transfer": True,
            "normalization": {
                "cost_scale": 1.0,
                "distance_scale": 1.0
            },
            "risk_measures": {
                "variance_guard": 0.01,
                "max_incremental_cost": 1.5
            }
        },
        "interpretability": {
            "explanation": "Deterministic greedy build with budget check and simple constraints. No replay memory.",
            "log_messages": False
        },
        "determinism": True,
        "parameters": {
            "origin_policy": "fixed_origin_index_0",
            "greedy_tie_breaker": "lowest_incremental_cost",
            "visited_handling": "no_revisit",
            "max_steps": None
        },
        "compatibility": {
            "tsplib_compatibility": True,
            "synthetic_compatibility": True
        }
    }
    return scaffold
