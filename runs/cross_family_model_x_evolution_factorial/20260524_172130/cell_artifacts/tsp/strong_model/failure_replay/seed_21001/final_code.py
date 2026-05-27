def build_heuristic():
    return {
        "name": "failure_replay_candidate_1",
        "technique": "failure_replay",
        "description": "Interpretable TSP heuristic scaffold with conservative local search and adaptive candidate selection.",
        "objectives": {
            "primary": "held_out_generalization",
            "secondary": ["robustness", "interpretability", "synthetic_transfer"]
        },
        "components": {
            "construction": {
                "method": "nearest_neighbor",
                "start_policy": "multi_start_extremes",
                "starts": ["min_x", "max_x", "min_y", "max_y"],
                "tie_break": "lexicographic"
            },
            "candidate_selection": {
                "method": "restricted_candidate_list",
                "k": 12,
                "metric": "euclidean",
                "include_nn_backedges": True
            },
            "local_search": {
                "moves": ["2-opt", "node_reinsertion"],
                "acceptance": "first_improvement",
                "max_passes": 4,
                "stop_on_no_improve": True
            },
            "failure_replay": {
                "enabled": True,
                "archive_size": 0,
                "replay_policy": "none_yet",
                "use_cases": ["avoid_repeated_edge_crossings", "preserve_hard_instance_patterns"]
            }
        },
        "robustness": {
            "regularization": {
                "prefer_short_edges": True,
                "penalize_crossings": True,
                "penalty_weight": 1.0
            },
            "transfer_bias": {
                "scale_invariant": True,
                "instance_size_aware": True,
                "sparse_graph_friendly": True
            }
        },
        "parameters": {
            "deterministic": True,
            "seed": 0,
            "max_runtime_hint": "moderate",
            "complexity": "low"
        }
    }
