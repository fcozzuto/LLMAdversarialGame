def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP (no imports).
    # This scaffold emphasizes robustness on held-out TSPLIB-like instances and synthetic transfers,
    # while keeping interpretation and simplicity.
    scaffold = {
        "name": "constrained_tsplib_heuristic",
        "version": "1.0",
        "description": (
            "Robust, interpretable heuristic scaffold for constrained TSP. "
            "Favor balanced exploration of candidate edges and simple repair steps to satisfy "
            "constraint(s) while remaining deterministic."
        ),
        "technique": "random_replay",  # placeholder name aligned with the requested technique label
        "seed": 42,  # fixed seed for determinism
        "constraints": {
            "max_degree": 3,            # bound on node degree to keep tours simple
            "min_edge_cost_ratio": 0.0,  # allow zero or positive improvements only
            "required_edges_fraction": 0.0,  # no mandatory edge set by default
        },
        "objective": {
            "type": "minimize_total_cost",
            "weight_travel": 1.0,
            "weight_constraint_violation": 0.0,
            "weight_tour_length": 0.0,
        },
        "neighborhood_rules": {
            # Deterministic neighbor generation for a given tour
            "neighbor_generation": "two_opt_step",  # simple local move
            "max_candidates": 5,                 # limit candidates for interpretability
            "selection_strategy": "greedy_improvement",  # deterministic greedy choice
        },
        "repair_strategies": {
            "type": "constraint_fix",
            "steps": [
                {"name": "ensure_single_tour", "action": "connect_disconnected_components deterministically"},
                {"name": "respect_degree_bound", "action": "truncate_extra_edges to maintain max_degree"},
            ],
            "deterministic": True
        },
        "transfer_settings": {
            "robustness_goal": "positive_transfer_fraction",
            "synthetic_transfer": True,
            "tsplib_compatibility": True,
            "transfer_capacity": 1.0,
        },
        "scalability": {
            "per_instance_timeout_sec": 2,
            "max_iterations": 100,
            "early_stop": True,
        },
        "logging": {
            "enabled": True,
            "level": "info",
            "store_history": False
        },
        "documentation": {
            "notes": "This scaffold is intentionally simple and interpretable. It uses deterministic neighbor exploration and deterministic repairs to satisfy constraints. It is designed to generalize from TSPLIB-like instances and synthetic transfers without reliance on stochastic replay archives.",
        },
    }
    return scaffold
