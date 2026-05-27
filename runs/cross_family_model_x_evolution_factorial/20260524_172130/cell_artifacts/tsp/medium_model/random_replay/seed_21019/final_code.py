def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP using a simple,
    # interpretable strategy with deterministic "random_replay" style guidance.
    # Includes held-out TSPLIB-compatible structure and synthetic transfer hints.
    return {
        "name": "deterministic_constrained_tsp_heuristic_v1",
        "version": 1,
        "technique": "random_replay",
        "description": (
            "A robust, interpretable constrained TSP heuristic scaffold. "
            "Deterministic replay-like guidance to favor diverse held-out "
            "TSPLIB and synthetic transfer test cases while remaining "
            "simple and explainable."
        ),
        "parameters": {
            "seed": 1,  # fixed seed for determinism
            "route_building": "greedy_with_constraint_checks",
            "constraint_handling": "node_departure_limit_and_region_bounds",
            "neighborhood_strategy": "nearest_neighbor_with_backbone",
            "backbone_size": 4,  # fixed core path length to force structure
            "deterministic_replay": True,
            "replay_blocks": [
                # Predefined deterministic replay blocks (empty to indicate none yet)
            ],
            "tsplib_heldout_split": {
                "train_fraction": 0.7,
                "heldout_fraction": 0.3,
                "random_seed": 1
            },
            "synthetic_transfer_targets": [
                {
                    "type": "synthetic",
                    "shape": "balanced_degree",
                    "scale": 1.0
                }
            ],
        },
        "scaffolds": {
            "high_level": [
                "build a backbone path of fixed length",
                "insert constrained detours to satisfy region bounds",
                "verify subtour elimination and feasibility",
                "evaluate against held-out TSPLIB-like size classes",
            ],
            "stepwise_checks": [
                "feasibility_of_each_edge",
                "constraint_violation_guard",
                "cycle_free_path",
                "tour_complete_check",
            ],
        },
        "output": {
            "format": "list_of_node_indices_in_order",
            "feasibility_checks": [
                "is_tour",
                "is_feasible_with_constraints",
            ],
            "expected_performance": {
                "heldout_transfer_success_rate": "stable_low_variance",
                "tsplib_like_variants": "robust_across_sizes_20-200",
            }
        }
    }
