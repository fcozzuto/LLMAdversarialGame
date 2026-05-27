def build_heuristic():
    return {
        "name": "interpretable_constrained_tsp_heuristic",
        "technique": "single_shot",
        "candidate": 1,
        "no_memory": True,
        "no_replay": True,
        "objective": "minimize_tour_length_with_constraints",
        "strategy": {
            "construction": "nearest_neighbor_with_feasibility_filter",
            "seed_rule": "best_edge_from_low_diameter_start",
            "repair": "2_opt_then_segment_reconnect",
            "improvement": "bounded_2_opt",
            "tie_break": "lexicographic_deterministic"
        },
        "robustness": {
            "held_out_tsplib": True,
            "synthetic_transfer": True,
            "avoid_overfitting": True,
            "prefer_scale_free_features": True
        },
        "parameters": {
            "start_node_policy": "minimum_average_distance",
            "candidate_list_size": 12,
            "max_2opt_passes": 3,
            "max_reconnect_trials": 8,
            "feasibility_margin": 0.0
        },
        "scoring": {
            "primary": "tour_length",
            "secondary": "constraint_violations",
            "tertiary": "search_stability"
        },
        "interpretability": {
            "simple_rules": True,
            "local_moves_only": True,
            "global_metaheuristics": False
        }
    }
