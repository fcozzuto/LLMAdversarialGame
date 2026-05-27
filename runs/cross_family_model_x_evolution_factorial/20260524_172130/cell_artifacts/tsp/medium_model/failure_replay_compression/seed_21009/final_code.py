def build_heuristic():
    # Deterministic heuristic scaffold specification for constrained TSP (no imports).
    # This is a lightweight, interpretable scaffold focusing on robustness across TSPLIB-like
    # and synthetic transfer performance, with a clear failure_replay_compression structure.
    scaffold = {
        "name": "constrained_tsp_heuristic_scaffold_v1",
        "version": 1,
        "description": (
            "Robust, interpretable constrained TSP heuristic scaffold. "
            "Uses a deterministic sequence of phases with simple, readable rules "
            "and a compact failure_replay_compression store."
        ),
        "config": {
            # Core algorithmic strategy identifiers
            "phases": [
                "feasibility_filter",        # prune infeasible edge choices
                "greedy_seed_extension",     # build route from a seed
                "feasible_local_improvement",# small local swaps within feasibility
                "termination_check"           # stop if no improvement or max length reached
            ],
            # Edge/route selection parameters
            "edge_scoring": {
                "type": "lexicographic",
                "tie_breaker": "lowest_index",
                "disallow_exceeding_capacity": True
            },
            # Constraint handling
            "constraints": {
                "max_route_length": None,          # no absolute limit unless provided per instance
                "must_include_nodes": [],          # required nodes (if any)
                "must_exclude_nodes": []           # forbidden nodes (if any)
            },
            # Heuristic controls
            "limits": {
                "max_iterations": 100,
                "max_steps_per_iteration": 50,
                "time_budget_seconds": None
            },
            # Transferability considerations (robustness across instances)
            "transfer": {
                "train_on_training_instances": False,
                "use_synthetic_transfer": True,
                "transfer_noise_model": "none"  # kept minimal for determinism
            }
        },
        "data_structures": {
            # Minimal, transparent representations
            "distance_matrix": "placeholder_for_distance_matrix",  # to be supplied by caller
            "visited_flags": "sequence_of_boolean_flags",
            "current_path": "list_of_node_indices_in_visit_order",
            "best_path": "list_of_node_indices_in_visit_order"
        },
        "failure_replay_compression": {
            # Deterministic, empty until a failure archive is produced
            "replay_archive": [],
            "compressor": {
                "strategy": "none",  # no archival compression performed in scaffold
                "parameters": {}
            },
            "replay_recovery": {
                "enabled": False,
                "fallback_behavior": "continue_with_fresh_run"
            }
            # Note: No replay entries are available yet (as per Candidate 1 description)
        },
        "interpretability": {
            "notes": (
                "Phases are staged and deterministic. The scoring is lexicographic with a "
                "clear tie-breaker. All parameters are explicit and have sensible defaults."
            ),
            "logging": {
                "enabled": True,
                "level": "INFO",
                "log_format": "%(phase)s - %(message)s"
            }
        }
    }
    return scaffold
