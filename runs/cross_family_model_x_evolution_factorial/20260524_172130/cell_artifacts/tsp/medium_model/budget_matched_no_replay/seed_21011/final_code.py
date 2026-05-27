def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic
    # Note: This is a simple, interpretable heuristic framework using a
    # budget_matched_no_replay-style design without any external state.
    heuristic = {
        "name": "constrained_tsp_budget_matcher_v1",
        "version": 1,
        "description": (
            "A robust, interpretable heuristic scaffold for constrained TSP. "
            "Balances travel cost with simple feasibility checks and budgets "
            "to ensure deterministic behavior across TSPLIB and synthetic data."
        ),
        "technique": "budget_matched_no_replay",
        "budget": {
            # Global budget in arbitrary distance units; kept deterministic
            "max_distance": 10000,
            # Per-edge cap to avoid pathological jumps
            "max_edge_cost": 1000,
            # A simple token budget to mimic resource constraints
            "edge_tokens": 10
        },
        "constraints": {
            # Example constraint set; can be extended with problem-specific constraints
            "time_window": False,
            "pickup_delivery": False,
            "capacity": {
                "enabled": False,
                "capacity_limit": None
            }
        },
        "heuristic_steps": [
            # Step 1: Build a deterministic reference tour using nearest-not-exceeding approach
            {
                "step": 1,
                "action": "initialize_start",
                "params": {"start_node": 0}
            },
            {
                "step": 2,
                "action": "greedy_extend",
                "params": {
                    "strategy": "nearest_neighbor_with_budget_check",
                    "budget_checks": True,
                    "tie_breaker": "lowest_index"
                }
            },
            # Step 3: Apply simple feasibility guardrails
            {
                "step": 3,
                "action": "enforce_constraints",
                "params": {
                    "constraint_guard": "distance_cap",
                    "max_edge_cost": 1000
                }
            },
            # Step 4: Close tour if feasible within budget
            {
                "step": 4,
                "action": "close_tour",
                "params": {"return_if_unclosed": False}
            },
            # Step 5: If tour violates overall budget, prune and restart with fallback
            {
                "step": 5,
                "action": "budget_fallback",
                "params": {"fallback_strategy": "split_and_join", "segments": 2}
            }
        ],
        "transfer_performance": {
            "robustness": {
                "tsplib": ["att48", "berlin52", "eil76"],
                "synthetic": ["synthetic_cluster_A", "synthetic_cluster_B"],
                "baseline_comparison": "train_vs_validate_consistency"
            },
            "scalability": {
                "n_nodes_extrapolation": "linear",
                "expected_runtime": "O(n^2) in naive steps, with pruning reduces in practice"
            }
        },
        "interpretability": {
            "summary": "A deterministic, easy-to-audit heuristic with explicit budgets and simple steps.",
            "key_parameters": ["max_distance", "max_edge_cost", "edge_tokens"],
            "decision_logs": False
        },
        "determinism": True
    }
    return heuristic
