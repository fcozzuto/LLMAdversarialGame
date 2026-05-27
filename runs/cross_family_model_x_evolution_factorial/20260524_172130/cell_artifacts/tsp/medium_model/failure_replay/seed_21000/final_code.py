def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic.
    # This scaffold emphasizes robustness with held-out TSPLIB-like and synthetic transfer considerations.
    # No external imports; purely self-contained configuration dictionary.

    heuristic = {
        # Meta information
        "name": "robust_constrained_tsp_heuristic_v1",
        "version": 1,
        "description": (
            "A deterministic, interpretable scaffold for a constrained TSP heuristic. "
            "Designed to generalize beyond training instances by integrating simple, robust components."
        ),
        "author": "generate-by-chatgpt",
        "license": "MIT",
        "random_seed": 42,  # kept for deterministic behavior without relying on runtime randomness
        # Problem framing
        "problem_class": "constrained_tsp",
        "constraints": {
            "max_route_length": None,      # None implies no explicit global cap; can be set per instance
            "must_visit_nodes": "optional",# policy: if provided, enforce visiting required nodes
            "node_gain": 1.0,               # surrogate objective gain per visited node
        },
        # Heuristic components (interpretable, simple)
        "components": [
            {
                "name": "nearest_neighbor_with_constraint",
                "description": (
                    "Traverse by nearest unused node that satisfies local constraint feasibility. "
                    "If constraint violated, backtrack to last feasible step."
                ),
                "parameters": {
                    "lookahead": 1,
                    "max_steps": 1000,
                    "constraint_check": "local_feasibility",
                },
            },
            {
                "name": "path_pruning",
                "description": (
                    "After building a path, prune obvious detours that do not affect feasibility "
                    "or objective value using simple local checks."
                ),
                "parameters": {
                    " prune_tolerance": 1e-6,
                    "enable_swap_improvement": False,
                },
            },
            {
                "name": "fallback_shortest_paths",
                "description": (
                    "When the normal greedy path stalls, connect remaining nodes using the product "
                    "of a simple chart of precomputed synthetic distances. Ensures termination."
                ),
                "parameters": {
                    "strategy": "direct_connect",
                    "distance_metric": "euclidean_approx",
                },
            },
        ],
        # Transfer robustness considerations
        "transfer_settings": {
            "held_out_tsplib_like": True,
            "synthetic_transfer": True,
            "transfer_protocol": "deterministic_schedule",
            "donor_split_ratio": 0.5,
            "evaluation_focus": ["generalization_to_held_out_problems", "robust_feasibility"],
        },
        # Evaluation scaffolding (deterministic, minimal)
        "evaluation": {
            "train_eval_mode": False,
            "holdout_sets": {
                "tsplib_like": {
                    "example_size": 50,
                    "seed": 9999,
                    "description": "Deterministic held-out TSPLIB-like instances",
                },
                "synthetic_transfer": {
                    "example_size": 40,
                    "seed": 12345,
                    "description": "Synthetic instances for transfer robustness",
                },
            },
            "metrics": ["feasibility", "solution_cost", "runtime"],
        },
        # Output expectations
        "outputs": {
            "routes": "list_of_node_sequences",
            "status": "feasible|infeasible|partial",
            "summary": {
                "visited_nodes": "int",
                "path_length": "float",
                "cost": "float",
            },
        },
        # Deterministic behavior controls
        "determinism": {
            "seeded_random": True,
            "shuffle": False,
            "reproducibility_hardened": True,
        },
        # Debug and observability
        "debug": {
            "log_level": "WARNING",
            "trace_steps": False,
            "diagnostics": ["local_feasibility_checks", "path_pruning_checks"],
        },
    }

    return heuristic
