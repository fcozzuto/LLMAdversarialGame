def build_heuristic():
    # Deterministic constrained TSP heuristic scaffold
    # Purpose: provide a robust, interpretable heuristic framework with
    # held-out TSPLIB and synthetic transfer considerations.
    #
    # Structure:
    # - constraints: problem constraints to respect (e.g., distance bounds, subtour elimination)
    # - components: modular heuristic components with simple, interpretable behavior
    # - evaluation: deterministic metrics and failure_replay-style fallback
    #
    # This scaffold avoids imports and remains lightweight and explainable.

    heuristic = {
        "name": "deterministic_constrained_tsp_heuristic",
        "description": (
            "A deterministic scaffold combining a simple nearest-neighbor style expansion with "
            "budgeted improvements and explicit constraint checks. Designed for robustness "
            "across TSPLIB-like and synthetic instances, with a clear failure-replay path."
        ),
        "version": "1.0",
        "constraints": {
            # Example constraints for a generic constrained TSP
            "max_subtour_length": None,      # None => no hard limit to subtour length unless set
            "must_visit_all_nodes": True,
            "distance_symmetry": True,        # assume symmetric distances if available
            "max_iterations": 1000,            # deterministic cap to avoid infinite loops
            "avoid_revisiting_node": True,
        },
        "preprocessing": {
            # Deterministic preprocessing steps
            "normalize_distances": False,      # keep as-is to preserve TSPLIB scales
            "unit_scale": 1.0,
            "shuffle_seed": 42,                # fixed seed for reproducibility (no randomness)
            "edge_candidate_selection": "greedy"  # simple, deterministic method
        },
        "components": {
            "start_node_selection": {
                "method": "lowest_index_node",
                "description": "Start at the node with the smallest index to ensure determinism."
            },
            "greedy_extension": {
                "method": "nearest_unvisited",
                "description": (
                    "Expand tour by always selecting the nearest unvisited node that doesn't violate constraints."
                ),
                "tie_breaker": "lowest_index",
            },
            "local_improvement": {
                "method": "2-opt",
                "description": (
                    "Apply a simple 2-opt style improvement pass in a deterministic manner."
                ),
                "iterations": 10,
            },
            "constraint_checking": {
                "method": "explicit_subtour_check",
                "description": "After each step, ensure no subtours and all constraints satisfied.",
            }
        },
        "execution_flow": [
            "initialize_tour",
            "select_start_node",
            "greedy_extension",
            "local_improvement",
            "verify_constraints",
            "finalize_solution"
        ],
        "evaluation": {
            "deterministic_metrics": [
                "tour_length",
                "subtour_count",
                "constraint_violations"
            ],
            "fallback_policy": "failure_replay_like",
            "failure_replay_like": {
                "enabled": True,
                "notes": (
                    "If a constraint violation or no progress is detected, revert to a deterministic "
                    "fallback path using the precomputed or initial feasible tour if available."
                ),
            }
        },
        "transparency": {
            "log_every_step": True,
            "step_descriptions": True
        },
        "synthetic_transfer_considerations": {
            "transfer_robustness": {
                "assumed_domains": ["TSPLIB-like", "synthetic_transfer"],
                "evaluation_category": ["robustness", "generalization"],
                "policy": "favor_consistent_performance_across_domains"
            }
        },
        "notes": (
            "This is a minimal, interpretable scaffold intended for deterministic behavior. "
            "No randomness is introduced beyond fixed seeds. The structure is designed to be "
            "extended with concrete distance data structures without altering the core flow."
        )
    }

    return heuristic
