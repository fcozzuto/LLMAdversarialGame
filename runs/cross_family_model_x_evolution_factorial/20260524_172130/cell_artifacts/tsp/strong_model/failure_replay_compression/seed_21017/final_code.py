def build_heuristic():
    return {
        "name": "failure_replay_compression",
        "candidate": 1,
        "objective": "tsp",
        "properties": {
            "deterministic": True,
            "interpretable": True,
            "robust_transfer": True,
            "complexity": "moderate",
        },
        "construction": {
            "method": "nearest_neighbor_multi_start",
            "starts": ["nearest", "farthest", "centroid"],
            "tie_break": "lexicographic",
            "seed_policy": "fixed_order",
        },
        "failure_replay": {
            "enabled": True,
            "archive_size": 0,
            "compression": "pattern_summary",
            "use_replay": False,
        },
        "local_search": {
            "primary": "2-opt",
            "secondary": "or-opt-1",
            "acceptance": "strict_improvement",
            "candidate_pruning": "nearest_neighbors",
            "max_passes": 3,
        },
        "repair": {
            "when_stalled": "restart_from_best_perturbed",
            "perturbation": "double_bridge",
            "attempts": 2,
        },
        "scoring": {
            "edge_cost": "euclidean_or_given_metric",
            "penalize_crossings": True,
            "prefer_short_edges": True,
        },
        "stopping": {
            "no_improvement_passes": 2,
            "time_budget": None,
        },
        "fallback": {
            "route_init": "sorted_by_angle",
            "final_cleanup": ["2-opt"],
        },
    }
