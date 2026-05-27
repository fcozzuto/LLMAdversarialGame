def build_heuristic():
    return {
        "name": "deterministic_simple_heuristic",
        "seeder": "fixed_seed_42",
        "preprocessing": {
            "normalize_distances": True,
            "symmetrize": True
        },
        "initialization": {
            "method": "nearest_neighbor",
            "start_node": 0
        },
        "search": {
            "method": "2opt",
            "iterations": 100,
            "acceptance": "improvement_only"
        },
        "termination": {
            "max_time_seconds": 600,
            "max_iterations": 1000
        },
        "postprocessing": {
            "apply_2opt": True,
            "apply_3opt": False
        },
        "heuristic_parameters": {
            "candidate_list_size": 20,
            "local_search_only": True
        }
    }

