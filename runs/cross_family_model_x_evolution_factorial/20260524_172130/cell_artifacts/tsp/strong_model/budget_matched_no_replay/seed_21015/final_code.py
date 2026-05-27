def build_heuristic():
    return {
        "name": "budget_matched_no_replay",
        "type": "tsp_heuristic_scaffold",
        "deterministic": True,
        "replay": False,
        "memory": {
            "prior_candidates": False,
            "failure_memory": False,
            "compression": False,
        },
        "construction": {
            "method": "nearest_neighbor",
            "seeds": ["farthest_pair", "x_extreme", "y_extreme"],
            "tie_break": "lexicographic",
            "start_selection": "best_of_seeds",
        },
        "improvement": {
            "primary": "2_opt",
            "secondary": "or_opt_1",
            "acceptance": "first_improvement",
            "candidate_pruning": "nearest_neighbor_list",
            "candidate_list_size": 20,
            "crossing_focus": True,
        },
        "budgeting": {
            "budget_model": "matched_to_n",
            "move_budget": "8n^2",
            "edge_scan_budget": "24n",
            "restart_budget": 3,
        },
        "robustness": {
            "multi_start": True,
            "start_count": 4,
            "instance_scaling": "normalize_by_mean_edge_length",
            "fallback": "best_constructed_tour",
        },
        "interpretability": {
            "complexity": "moderate",
            "notes": [
                "Use multiple simple deterministic starts.",
                "Apply bounded local search with 2-opt and light 1-node relocation.",
                "Prefer short-edge candidates for transfer robustness.",
            ],
        },
    }
