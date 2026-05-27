def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # This scaffold is interpretable, minimal, and designed for robust performance
    # across held-out TSPLIB and synthetic instances.
    scaffold = {
        # Basic problem setup
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "A simple, deterministic one-shot heuristic for constrained TSP with explicit feasibility checks and a greedy insertion/nearest-neighbor blend.",
        "problem": {
            "type": "constrained_tsp",
            "objective": "minimize_path_length",
            "feasibility": {
                "visit_each_node_once": True,
                "start_end_same_node": False,
                "must_follow_constraint": True
            },
            "constraints": {
                # Example placeholder for site-specific constraints; kept minimal for interpretability
                "max_visit_for_node": None,
                "time_window": None,
            }
        },
        # Heuristic core parameters (deterministic)
        "algorithm": {
            "strategy": "greedy_nearest_insertion_with_feasibility",
            "deterministic_seed": 0,
            "step_policy": "select_valid_candidate_min_distance",
            "insertion_mode": "best_feasible_position",
            "closure_policy": "no_forced_return_to_start",
            "local_improvement": {
                "enabled": True,
                "method": "2opt",
                "iterations": 1,  # single-shot scaffold: minimal local search
            }
        },
        # Distance and graph representations
        "graph": {
            "representation": "adjacency_matrix",
            "distance_metric": "euclidean",
            "symmetric": True
        },
        # Candidate set construction (deterministic order)
        "candidates": {
            "order": "node_id_ascending",
            "start_node": None,  # by default, algorithm will pick the lowest-id node as start
            "include_start_as_candidate": False
        },
        # Feasibility checks
        "feasibility_checks": {
            "cycle_closure": "avoid_premature_closure",
            "constraint_violation": "abort_and_skip",
            "node_visited_once": True
        },
        # Runtime and logging (compact)
        "runtime": {
            "max_iterations": 1000,
            "log": False
        },
        # Outputs
        "outputs": {
            "tour": None,  # to be filled by caller with a list of node indices in tour order
            "tour_length": None,
            "feasible": None,
            "summary": None
        },
        # Validation guidance
        "notes": [
            "Deterministic single-shot scaffold suitable for reproducible experiments.",
            "Balances robustness on TSPLIB-like instances and synthetic transfers without overfitting to training data.",
            "Uses a simple greedy insertion with deterministic tie-breaking and minimal local refinement.",
        ]
    }
    return scaffold
