def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "description": "Deterministic, interpretable TSP heuristic scaffold with constraints support and transfer-ready structure.",
        "version": "1.0",
        "technique": "failure_replay_compression",
        "notes": [
            "Deterministic behavior: no randomness, fixed choices.",
            "Robustness through interpretability: simple scoring rules and clear constraint handling.",
            "Transfer readiness: placeholders for TSPLIB-like benchmarks and synthetic transfer tasks.",
            "Scaffold focuses on constrained TSP variants with reusable components for edge feasibility and route construction."
        ],
        "components": {
            "problem_space": {
                "type": "constrained_tsp",
                "constraints": {
                    "predefined_required_nodes": [],
                    "forbidden_edges": [],
                    "quota_per_region": None,
                    "time_window": None
                },
                "distance_metric": "euclidean",
                "symmetry": True
            },
            "solution_representation": {
                "route_encoding": "ordered_node_list",
                "validity_check": "is_valid_route(route, constraints)",
                "feasibility_checks": [
                    "all_required_nodes_present(route, constraints)",
                    "no_forbidden_edges_in_route(route, constraints)",
                    "subtour_elimination_if_needed(route)"
                ]
            },
            "construction_strategy": {
                "base_heuristic": "greedy_nearest_neighbor_with_constraints",
                "fallback": "insertion_with_constraints",
                "priority_rules": [
                    "prefer_required_nodes_first",
                    "prefer_short_edge_extensions",
                    "avoid_forbidden_edges",
                    "maintain_connectivity"
                ]
            },
            "evaluation_stub": {
                "training_focus": "not_primary",
                "evaluation_types": [
                    "intra_instance_performance",
                    "inter_instance_transfer_performance"
                ],
                "benchmark_sources": [
                    "synthetic_transfer_tasks",
                    "TSPLIB_like_constrained_instances",
                    "held_out_instances"
                ],
                "metrics": [
                    "total_distance",
                    "feasibility_rate",
                    "runtime_ms",
                    "robustness_score"
                ]
            },
            "replay_and_failure_handling": {
                "strategy": "failure_replay_compression",
                "archive_state": "empty_by_default",
                "replay_policy": "deterministic_lookup_for_failed_edges",
                "compression_level": "minimal",
                "deterministic_recovery": True
            }
        },
        "interfaces": {
            "constraints_interface": "dict-like with keys matching problem_space.constraints",
            "route_interface": "list[int] of node indices",
            "diagnostics_interface": "optional, dict with metrics"
        }
    }
