def build_heuristic():
    return {
        "name": "failure_replay_candidate_1",
        "technique": "failure_replay",
        "target": "constrained_tsp",
        "properties": {
            "deterministic": True,
            "interpretable": True,
            "complexity": "low",
            "transfer_focus": "held_out_tsplib_and_synthetic",
        },
        "construction": {
            "initial_tour": "nearest_neighbor",
            "start_node": "fixed_min_index",
            "tie_break": "lexicographic",
        },
        "local_search": {
            "primary_moves": ["2-opt", "relocate"],
            "move_order": ["2-opt", "relocate"],
            "candidate_set": "nearest_neighbors",
            "candidate_k": 20,
            "first_improvement": True,
            "max_passes": 3,
        },
        "constraints": {
            "respect_constraints_during_moves": True,
            "repair_strategy": "minimal_patch",
            "infeasible_move_penalty": 10**9,
        },
        "failure_replay": {
            "enabled": True,
            "archive_entries": [],
            "replay_policy": "none_available",
            "update_rule": "record_failed_edges_and_infeasible_segments",
        },
        "acceptance": {
            "strategy": "greedy",
            "allow_equal": False,
        },
        "termination": {
            "max_no_improvement_passes": 2,
            "time_budget_scaling": "moderate",
        },
        "scoring": {
            "objective": "tour_length",
            "secondary": ["feasibility", "stability"],
            "edge_penalty_mode": "additive",
        },
    }
