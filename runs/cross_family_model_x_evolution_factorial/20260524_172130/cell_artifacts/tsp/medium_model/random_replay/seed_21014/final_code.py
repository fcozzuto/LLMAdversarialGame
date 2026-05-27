def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic using a "random_replay" style
    # with no external imports and a simple, interpretable structure.
    heuristic = {
        "name": "constrained_tsp_scaffold_random_replay",
        "version": "1.0",
        "description": (
            "Deterministic TSP heuristic scaffold using a small, interpretable "
            "set of components: distance function, constraint checks, and a "
            "held-out replay-like strategy for path construction."
        ),
        "technique": "random_replay",
        "components": {
            "distance": {
                "type": "euclidean_2d",
                "norm": "euclidean",
                "description": "Compute straight-line distance between points."
            },
            "constraints": [
                {
                    "type": "degree_limit",
                    "limit": 2,
                    "description": "Each city has at most two incident edges (cycle consistency)."
                },
                {
                    "type": "subtour_elimination",
                    "method": "simple_check",
                    "description": "Avoid subtours during incremental construction."
                }
            ],
            "initialization": {
                "seed": 0,
                "method": "nearest_neighbor_seed",
                "description": "Start from a fixed seed city and extend using a deterministic rule."
            },
            "extension_rule": {
                "type": "greedy_by_distance",
                "criterion": "min_distance",
                "tie_breaker": "lower_index",
                "description": "At each step, connect to the nearest feasible city under constraints."
            },
            "replay_strategy": {
                "type": "random_replay_like",
                "archive": [],
                "description": "Deterministic replay scaffold that would, in a full system, replay past decisions. Here, kept deterministic with fixed seed.",
                "seed": 0
            }
        },
        "parameters": {
            "city_count": None,
            "cities": "list of (x, y) coordinates to be supplied by caller",
            "constraints": {
                "degree_limit": 2,
                "subtour_elimination": True
            },
            "tuning": {
                "max_iterations": 100,
                "stop_if_no_improvement": True,
                "improvement_window": 5
            }
        },
        "evaluation": {
            "held_out_sets": {
                "tsplib_held_out": True,
                "synthetic_transfer": True
            },
            "metrics": ["tour_length", "feasibility", "subtour_count"],
            "robustness_focus": "balanced_performance_training_vs_holdout"
        },
        "interpretability": {
            "logics": [
                "greedy extension under constraints",
                "deterministic tie_breaker by city index",
                "clear subtour checks"
            ],
            "explanation_interface": "textual_root_cause",
        },
        "notes": "This scaffold is deterministic and interpretable. The actual random_replay entries would be populated by a replay archive in a full system; here there are none.",
    }
    return heuristic
