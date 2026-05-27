def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP with a "random_replay"-style approach.
    # This scaffold is designed to be robust across TSPLIB-like and synthetic transfer scenarios
    # while remaining interpretable and not overly complex. It does not rely on imports.

    # The dictionary below encodes:
    # - strategy_name: a readable name
    # - components: sequence of heuristic components with fixed parameters
    # - constraints: interpretation of hard constraints to satisfy
    # - evaluation: how to score candidate tours in a deterministic manner
    # - replay: placeholder for "random_replay" mechanism; since no archive exists, use a fixed seed path
    # - transfer: hints for cross-instance generalization
    # - logging: minimal metadata to aid debugging without external dependencies

    heuristic = {
        "strategy_name": "deterministic_random_replay_scaffold",
        "version": 1,
        "description": (
            "Deterministic scaffold combining simple constructive tour with constraint handling "
            "and a fixed, replay-like path selection to simulate exploration without randomness."
        ),
        "components": [
            {
                "name": "seeded_nearest_neighbor",
                "params": {
                    "start_node_index": 0,
                    "distance_metric": "euclidean",
                    "tie_breaker": "lowest_index",
                    "seed": 42  # fixed seed to ensure determinism
                }
                # Note: This component is deterministic given the fixed seed and tie-break rules.
            },
            {
                "name": "projection_pruning",
                "params": {
                    "prune_fraction": 0.15,
                    "criteria": ["degree_limit", "subtour_elimination"]
                }
            },
            {
                "name": "cycle_completion",
                "params": {
                    "allow_incomplete_subtour_breaks": False,
                    "finalize_with_shortcuts": True
                }
            },
            {
                "name": "constraint_filter",
                "params": {
                    "hard_constraints": ["max_degree_2", "vehicle_capacity_limit"],
                    "soft_constraints": ["balance_tour_length", "spread_across_regions"],
                    "penalties": {
                        "violation": 1e6,
                        "short_subtour": 1000
                    }
                }
            }
        ],
        "constraints": {
            "node_visit": "each_node_at_most_once",
            "cycle": "Hamiltonian_cycle_required",
            "subtour_elimination": True,
            "capacity_limit": True
        },
        "evaluation": {
            "objective": "minimize_tour_length_with_constraints",
            "scoring": [
                {"name": "tour_length", "weight": 1.0},
                {"name": "constraint_violations", "weight": 2.0},
                {"name": "balance_score", "weight": 0.5}
            ],
            "normalization": {
                "tour_length": "relative_to_min_possible",
                "constraint_violations": "penalize_heavy_violations"
            }
        },
        "replay": {
            "mode": "random_replay",
            "archive_available": False,
            "seed": 42,
            "paths": [
                # Placeholder deterministic path IDs representing a replay-like sequence
                "path_A_fixed_seed",
                "path_B_fixed_seed"
            ],
            "policy": "greedy_fixed_tour_construction",
            "notes": "Since no replay archive exists, use fixed deterministic policy conforming to seed."
        },
        "transfer": {
            "robustness_targets": ["TSPLIB_like_instances", "synthetic_transfer_sets"],
            "generalization_strategies": [
                "normalize_city_counts",
                "balance_region_density",
                "consistent_constraint_handling_across_domains"
            ],
            "expected_performance": {
                "intra_domain": "competitive",
                "inter_domain_transfer": "stable_but_world_changes_resistant"
            }
        },
        "logging": {
            "enabled": True,
            "level": "info",
            "trace": {
                "record_steps": True,
                "record_tour_lengths": True
            }
        }
    }

    return heuristic
