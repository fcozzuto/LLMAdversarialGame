def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for a constrained TSP heuristic with robust evaluation.",
        "concept": {
            "objective": "minimize tour length while respecting per-node or per-arc constraints",
            "strategy": "hybrid: constructive + local improvement with simple feasibility checks",
            "interpretability": "high",
        },
        "methodology": {
            "construction": {
                "type": "greedy_construct",
                "start_node_selection": "lowest_index",
                "feasible_arcs": "pre-filtered_by_constraints",
                "tie_break": "lowest_incremental_cost",
                "step_check": "feasibility_of_partial_tour",
            },
            "local_improvement": {
                "type": "2-opt",
                "acceptance": "improves_cost and preserves_constraints",
                "limit": 100  # deterministic bound for robustness
            },
            "constraints": {
                "node_constraints": "each_node_must_be_visited_at_mappropriate_times_or_not_exceed_limits",
                "edge_constraints": "specific_arcs_allowed_or_disallowed",
                "subtour_constraints": "avoid_subtours_when_required",
            },
        },
        "data_requirements": {
            "tsplib_like_instances": True,
            "synthetic_transfer_instances": True,
            "instance_representation": {
                "nodes": "index_and_coordinates_or_costs",
                "edges": "optional_cost_matrix_if_available",
                "constraints": "admissible_sets_or_bounds_per_node_or_edge"
            }
        },
        "robustness_and_validation": {
            "replay_failure_handling": "failure_replay_compression_placeholder",
            "evaluation_metrics": [
                "tour_cost",
                "feasibility_rate",
                "constraint_violation_count",
                "transfer_performance_across_domains"
            ],
            "determinism": True
        },
        "scalability": {
            "approach": "linear-ish_construct_with_local_improvement_bounds",
            "per_instance_runtime_bound_ms": 250
        },
        "notes": [
            "No external imports; fully self-contained scaffold.",
            "Uses straightforward, interpretable heuristics suitable for TSPLIB-like and synthetic transfer scenarios.",
            "Failure replay compression placeholder included to align with the specified technique."
        ]
    }
