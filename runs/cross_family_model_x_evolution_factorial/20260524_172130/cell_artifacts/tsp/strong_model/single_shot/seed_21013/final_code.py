def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "type": "tsp_heuristic_scaffold",
        "strategy": "nearest_neighbor_with_2opt_refinement",
        "deterministic": True,
        "transfer_bias": "robust_generalization",
        "interpretability": "high",
        "complexity": "moderate",
        "construction": {
            "rule": "nearest_neighbor",
            "start_rule": "farthest_from_centroid",
            "tie_break": "lexicographic",
        },
        "refinement": {
            "rule": "2opt",
            "max_passes": 3,
            "first_improvement": True,
            "candidate_pruning": "nearest_k",
            "k": 20,
        },
        "scoring": {
            "distance_metric": "euclidean",
            "objective": "tour_length",
        },
        "safeguards": {
            "avoid_overfitting": True,
            "prefer_global_structure": True,
            "held_out_robustness": True,
        },
    }
