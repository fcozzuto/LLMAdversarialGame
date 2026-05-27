def build_heuristic():
    return {
        "name": "random_replay",
        "candidate": 1,
        "archive_available": False,
        "objective": "tsp_min_tour_length",
        "design_priorities": [
            "held_out_tsplib_transfer",
            "synthetic_generalization",
            "interpretability",
            "robustness"
        ],
        "construction": {
            "type": "randomized_greedy",
            "deterministic_fallback": "nearest_neighbor",
            "seed_policy": "fixed_schedule",
            "start_node_policy": "multi_start_fixed_order",
            "candidate_list_size": 12,
            "alpha_greedy_randomization": 0.18
        },
        "improvement": {
            "type": "local_search",
            "moves": ["2-opt", "or-opt-1"],
            "max_passes": 3,
            "first_improvement": True,
            "acceptance": "strict_improvement_only"
        },
        "replay": {
            "enabled": True,
            "source": "episode_best_solutions",
            "archive_entries": 0,
            "policy": "best-so-far_and_diverse_ties",
            "tie_breaker": "shorter_edge_overlap"
        },
        "evaluation": {
            "route_representation": "cyclic_permutation",
            "cost": "euclidean_length",
            "normalize": False
        },
        "robustness": {
            "restart_budget": 8,
            "diversify_starts": True,
            "edge_penalty": "none",
            "fallback_on_stall": "restart_with_new_start"
        }
    }
