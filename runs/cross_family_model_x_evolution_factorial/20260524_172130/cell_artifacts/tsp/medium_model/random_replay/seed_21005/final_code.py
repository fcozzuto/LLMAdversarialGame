def build_heuristic():
    return {
        "name": "deterministic_constrained_tsp_heuristic",
        "version": 1,
        "description": "A robust, interpretable constrained TSP heuristic scaffold using deterministic guidance and a random_replay-inspired structure without external imports.",
        "technique": "random_replay",
        "seed": 42,
        "instances": {
            "source": ["TSPLIB", "synthetic_transfer"],
            "constraints": {
                "max_distance_ratio": 1.5,
                "mandatory_nodes": [],
                "forbidden_edges": [],
                "budget": None  # None implies unconstrained budget in scaffold
            },
        },
        "planning": {
            "steps": [
                "initialize_cluster_centroids deterministically",
                "build feasible neighborhood graph respecting constraints",
                "select starting node via deterministic tie-breaking (lowest id)",
                "greedy_extend_with_feasible_edge_order",
                "apply simple 2-opt local improvement with fixed iterations",
                "validate route feasibility against constraints",
                "store and return final tour with tour_cost"
            ],
            "edge_ordering": ["lowest_cost", "shortest_distance", "lexicographic_id"],
            "improvement_rounds": 5,
            "constraints_handling": {
                "avoid_mandatory_conflicts": True,
                "prefer_short_edges": True
            }
        },
        "representation": {
            "tour": ["node_id integers in order", "0 denotes return to start for cycle"],
            "cost": "sum of edge costs along tour according to a deterministic distance function",
            "feasible": True
        },
        "cost_model": {
            "distance_function": "predefined_dense_metric",
            "penalties": {
                "constraint_violation": 1e6
            }
        },
        "robustness": {
            "held_out_evaluation": "structure supports evaluation on held-out TSPLIB and synthetic transfer instances",
            "determinism": True,
            "reproducibility": True
        },
        "notes": [
            "This scaffold emphasizes interpretability.",
            "No external data loading or randomness beyond a fixed seed.",
            "No imports required."
        ],
        "random_replay_like": {
            "archive_entries": [],
            "replay_policy": "deterministic_simulation",
            "candidate_selection": "first_feasible_by_order"
        }
    }
