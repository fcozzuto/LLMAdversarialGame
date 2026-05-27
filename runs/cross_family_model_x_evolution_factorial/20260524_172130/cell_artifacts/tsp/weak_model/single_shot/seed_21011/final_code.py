def build_heuristic():
    return {
        "name": "single_shot_candidate_1",
        "technique": "single_shot",
        "candidate_id": 1,
        "description": "A simple deterministic heuristic selecting nearest unvisited neighbor with a threshold for accepting edges, balancing robustness and interpretability.",
        "steps": [
            {
                "action": "initialize",
                "parameters": {
                    "start_node": "node_0",
                    "visited": ["node_0"],
                    "path": ["node_0"]
                }
            },
            {
                "action": "loop_until_all_visited",
                "parameters": {
                    "condition": "len(visited) < total_nodes"
                }
            },
            {
                "action": "select_next_node",
                "parameters": {
                    "current_node": "last_in_path",
                    "candidate_nodes": "unvisited_nodes",
                    "selection_criteria": "minimum_distance_below_threshold",
                    "threshold": 1.5  # tunable parameter to balance robustness
                }
            },
            {
                "action": "add_node_to_path",
                "parameters": {
                    "node": "selected_node"
                }
            },
            {
                "action": "mark_node_visited",
                "parameters": {
                    "node": "selected_node"
                }
            }
        ],
        "parameters": {
            "distance_metric": "euclidean",
            "threshold": 1.5,
            "start_node": "node_0"
        },
        "robustness_criteria": "validated on TSPLIB and synthetic transfer performance",
        "interpretability": "the heuristic selects the nearest neighbor within a fixed threshold, making it easy to understand and tune."
    }

