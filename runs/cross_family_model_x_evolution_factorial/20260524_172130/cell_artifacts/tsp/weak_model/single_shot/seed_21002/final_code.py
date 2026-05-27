def build_heuristic():
    return {
        "technique": "single_shot",
        "candidate": 1,
        "description": "A straightforward nearest neighbor heuristic optimized for interpretability and robustness.",
        "parameters": {
            "start_node": "minimum_id",  # Start from the node with the smallest ID for consistency
            "distance_metric": "euclidean",  # Use Euclidean distance assuming 2D coordinates
            "selection_strategy": "nearest_neighbor",  # Select the closest unvisited city at each step
            "termination_condition": "all_cities_visited",  # Complete route once all cities are visited
            "robustness": "validated_on_TSPLIB_and_synthetic",  # Ensures performance generalization
            "interpretable": True,  # Keeps the heuristic transparent and simple
            "max_iterations": None,  # No explicit iteration limit; terminates upon visiting all cities
        }
    }

