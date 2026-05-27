def build_heuristic():
    # Deterministic heuristic scaffold for a constrained TSP (single-shot).
    # This scaffold emphasizes robustness across held-out TSPLIB-like instances
    # while remaining interpretable and lightweight.
    scaffold = {
        "name": "constrained_tsp_single_shot_heuristic",
        "version": 1,
        "technique": "single_shot",
        "description": (
            "A simple, interpretable constrained TSP heuristic. Starts from a feasible "
            "seed tour and performs a single pass of constructive improvements with "
            "pruning based on distance and feasibility constraints."
        ),
        "parameters": {
            "seed_strategy": "nearest_neighbor_from_start",
            "start_node": 0,
            "feasibility_checks": True,
            "max_iterations": 50,
            "local_improvement": "2-opt",
            "improvement_limit_per_step": 2,
            "balance_constraints": True,
            "penalty_for_infeasibility": 1.0,
            "distance_metric": "euclidean",
        },
        "feasibility_constraints": {
            "capacity_constraint": None,  # If provided, should be a numerical limit per route.
            "precedence_constraints": [],   # List of (a, b) meaning a must precede b
            "time_windows": None,           # Optional: {(node, start, end)}
            "vehicle_count": 1,               # Single-vehicle tour by default
            "subtour_elimination": True
        },
        "construction_phase": {
            "seed_tour": "build_seed_tour",
            "seed_tour_strategy": "nearest_neighbor",
            "allow_subtour": False,
            "greedy_selection": True,
            "shuffle_neighbors": False,
        },
        "improvement_phase": {
            "method": "2-opt",
            "applied_steps": 2,
            "acceptance_criterion": "improvement_only",
            "forbidden_swaps": [],
        },
        "algorithmic_assumptions": {
            "deterministic_seed": True,
            "no_randomness": True,
            "stable_runtime": True,
            "scalability_hint": "works well for medium-sized TSPLIB-like instances with modest constraints",
        },
        "output": {
            "tour": None,            # to be filled by the caller after execution
            "tour_cost": None,
            "feasibility_report": None
        },
        "compatibility": {
            "tsplib_style": True,
            "synthetic_transfer": True,
            "interpretability": True,
            "determinism": True
        }
    }
    return scaffold
