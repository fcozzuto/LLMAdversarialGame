def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP using a simple
    # random_replay-like structure without relying on imports or external data.
    # This scaffold emphasizes robustness to Held-Out TSPLIB-like instances
    # and synthetic transfer performance while staying interpretable.
    heuristic = {
        "name": "deterministic_random_replay_scaffold",
        "version": 1,
        "description": (
            "Deterministic scaffold for a constrained TSP heuristic using a "
            "random_replay-inspired structure. No external data dependencies; "
            "stable behavior across runs."
        ),
        "technique": "random_replay",
        "parameters": {
            "seed": 0,
            "initial_ordering": "greedy_by_distance",
            "segment_constraints": {
                "max_segment_length": 0.15,  # fraction of total tour length
                "min_unvisited_before_repeat": 2
            },
            "fallback_strategy": "nearest_neighbor",
            "insertion_strategy": "cheapest_insertion",
            "repair_strategy": "2-opt",
            "stop_condition": "complete_tour",
            "quality_metrics": ["length", "feasibility", "diversity"],
        },
        "data_pipelines": {
            "held_out_tsplib_styles": ["pr2392", "att48", "pcb3038", "eil51"],
            "synthetic_transfer_styles": ["clustered_points", "sparse_hubs"],
            "validation_protocol": {
                "train_split": 0.7,
                "held_out_split": 0.3,
                "evaluation_runs": 3
            }
        },
        "constraints": {
            "must_visit_order": None,  # optional precedence constraints can be plugged in
            "time_windows": None,        # placeholder for time window constraints
            "capacity": None             # placeholder for capacity constraints
        },
        "interpretability": {
            "log_per_step": True,
            "explanations": [
                "selected_next_by = 'cheapest_insertion' within allowed segment",
                "feasibility check enforced before adding an edge",
                "fallback to nearest_neighbor if no feasible insertions"
            ]
        },
        "random_replay_archive": {
            "entries": [],
            "replay_model": "deterministic_placeholder",
            "notes": "No replay archive entries are available yet."
        }
    }
    return heuristic
