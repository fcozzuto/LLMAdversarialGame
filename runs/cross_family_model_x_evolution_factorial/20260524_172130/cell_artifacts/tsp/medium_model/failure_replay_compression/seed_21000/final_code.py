def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "description": "Deterministic, interpretable TSP heuristic scaffold with held-out TSPLIB and synthetic transfer considerations.",
        "version": "1.0",
        "technique": "failure_replay_compression",
        "parameters": {
            "use_heldout_tsplib": True,
            "use_synthetic_transfer": True,
            "compression_level": 1,  # minimal compression to preserve interpretability
            "replay_archive_entries": 0,  # none available yet
            "deterministic_seed": 42,
            "neighborhood_size": 1,  # simple 1-step improvements
            "max_iterations": 100,
            "maximize_tour_quality_fraction": 0.95
        },
        "heuristic_components": [
            {
                "name": "initial_solution",
                "type": "greedy_consecutive",
                "description": "Construct an initial tour by visiting cities in index order with nearest-neighbor tie-breaking by lower index.",
                "parameters": {
                    "tie_breaker": "lower_index"
                }
            },
            {
                "name": "local_improvement",
                "type": "2_opt",
                "description": "Apply 2-opt local search with a fixed, small neighborhood to maintain simplicity and interpretability.",
                "parameters": {
                    "iterations": 20
                }
            },
            {
                "name": "constrained_feasibility",
                "type": "feasibility_enforcer",
                "description": "Ensure feasibility with respect to simple hard constraints (e.g., subtour elimination via a lightweight check).",
                "parameters": {
                    "subtour_elimination": "lightweight"
                }
            },
            {
                "name": "failure_replay_compression",
                "type": "compression",
                "description": "Record decision points and replay failed attempts minimally to guide future choices without complexity.",
                "parameters": {
                    "archive_size": 0  # no replay archive yet
                }
            }
        ],
        "constraints_considered": [
            "city_visitation_once",
            "subtour_free"
        ],
        "output_format": {
            "tour": "list[int]",
            "cost": "float",
            "log": "list[str]"
        },
        "robustness_notes": [
            "Deterministic seed ensures reproducibility across runs.",
            "Balanced emphasis on TSPLIB-heldout instances and synthetic transfer cases.",
            "Simple, interpretable steps preferred over opaque metaheuristics."
        ]
    }
