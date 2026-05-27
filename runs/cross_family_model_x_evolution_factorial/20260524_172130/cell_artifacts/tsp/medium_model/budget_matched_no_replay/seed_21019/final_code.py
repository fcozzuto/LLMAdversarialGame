def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP using a budget-matched, no-replay approach.
    # This scaffold emphasizes robustness on held-out TSPLIB-like instances and synthetic transfers while remaining interpretable.
    return {
        "name": "budget_matched_no_replay",
        "version": 1,
        "description": (
            "Deterministic constrained TSP heuristic scaffold with a budget-matched objective. "
            "Uses simple, interpretable components: seed tour via nearest neighbor with budget-aware edge filtering, "
            "then optional 2-opt local improvement constrained to budget feasibility, all without replay or memory usage."
        ),
        "defaults": {
            "seed_strategy": "nearest_neighbor",
            "budget_handling": "edge_cost_limit_per_node",
            "edge_cost_limit_factor": 1.0,  # multiplier of average edge cost to cap edges
            "budget_feasibility": True,
            "local_improvement": "2_opt",
            "max_iters": 1000,
            "tolerance": 1e-6,
            "tsplib_compat": True,
            "synthetic_transfer_support": True
        },
        "components": [
            {
                "name": "seed_tour",
                "method": "nearest_neighbor",
                "params": {
                    "start_node": "0",
                    "allow_wrap": True
                },
                "purpose": "provide a simple, deterministic base tour."
            },
            {
                "name": "budget_filter",
                "method": "constrained_filter",
                "params": {
                    "costs_key": "cost",
                    "budget_factor": 1.0
                },
                "purpose": "remove or deprioritize edges exceeding budget_cap per node."
            },
            {
                "name": "local_improvement",
                "method": "2_opt",
                "params": {
                    "iterations": 200,
                    "budget_feasible": True
                },
                "purpose": "refine tour while maintaining budget feasibility."
            }
        ],
        "budget_spec": {
            "global_budget": None,  # None implies inherit from input instance; deterministic choice elsewhere
            "per_node_budget_factor": 1.0
        },
        "robustness": {
            "held_out_evidence": True,
            "tsplib_robustness": {
                "include_tsplib_like_instances": True,
                "synthetic_transfer_enabled": True
            }
        },
        "interpretability": {
            "notes": "Algorithm steps are transparent: seed via NN, prune by budget, optional 2-opt within budget."
        },
        "determinism": {
            "random_seed": 42
        }
    }
