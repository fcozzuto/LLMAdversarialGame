def build_heuristic():
    # Deterministic scaffold for a constrained TSP heuristic using a simple
    # randomized-replay style outline without imports or external data.
    # This scaffold emphasizes robustness across held-out TSPLIB-like instances
    # and synthetic transfers, while staying interpretable.
    return {
        "name": "constrained_tsp_heuristic_scaffold_v1",
        "description": (
            "Deterministic heuristic scaffold using a simple constructive plus repair "
            "strategy with deterministic tie-breaking and constraint handling. "
            "Intended for evaluation with held-out TSPLIB-like instances and synthetic transfers."
        ),
        "version": 1,
        "technique": "random_replay",
        "replay_policy": {
            "enabled": True,
            "archive_entries": [],
            "seed": 0,  # deterministic seed in absence of an actual random module
            "replay_depth": 2,  # simple two-pass replay for robustness
            "tie_breaker": "lexicographic",  # deterministic tie-breaking
        },
        "construction_phase": {
            "strategy": "constructive_greedy_with_constraints",
            "initial_order": "nodes_sorted_by_id",
            "nearest_neighbor_step": {
                "enabled": True,
                "criterion": "distance",
                "cost_update": "incremental",
                "tie_breaker": "lexicographic",
            },
            "constraint_enforcement": {
                "capacity_limit": "edge_count <= 1 or per-node_degree <= 2",
                "forbidden_subpaths_check": True,
                "pruning": {
                    "enabled": True,
                    "min_gain_threshold": 0.0
                }
            },
            "local_improvement": {
                "enabled": True,
                "moves": ["2-opt", "3-opt", "swap"],
                "improve_until_no_better": True,
                "local_search_tie_breaker": "lexicographic",
            }
        },
        "transfer_mechanisms": {
            "robustness": {
                "transfer_across_instance_types": True,
                "scaling_considerations": "ignore_large_runtime_variants",
                "evaluation_metric": "overall_cost_improvement",
            },
            "synthetic_transfer": {
                "type": "parameter_shift",
                "parameters": {
                    "p_shift": 0.0,
                    "noise_scale": 0.0
                },
                " stability_checks": True
            }
        },
        "robustness_and_logging": {
            "logging_level": "INFO",
            "trace_sparsity": 0.0,
            "diagnostics": {
                "early_stopping": False,
                "timeout_guard": False
            }
        },
        "interpretability_features": {
            "decision_trace": True,
            "deterministic_tie_breaking": True,
            "human_readable_summary": True
        },
        "output_schema": {
            "path": None,
            "format": "json",
            "fields": [
                "solution_sequence",
                "tentative_cost",
                "constraints_satisfied",
                "replay_applied",
                "runtime_ms"
            ]
        }
    }
