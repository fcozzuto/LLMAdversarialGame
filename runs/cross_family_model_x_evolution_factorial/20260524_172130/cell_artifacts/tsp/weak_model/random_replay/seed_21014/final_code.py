def build_heuristic():
    return {
        "name": "simple_nearest_neighbor_with_optimization",
        "description": "A deterministic heuristic combining a nearest neighbor approach with a local improvement step to enhance solution quality.",
        "parameters": {
            "initial_construction": "nearest_neighbor",
            "local_search": "2opt",
            "max_iterations": 100,
            "refinement": True,
            "seed": 42
        },
        "strategy": {
            "construction_method": "construct_tour_nearest_neighbor",
            "local_optimization": "apply_2opt_until_convergence",
            "stop_condition": "max_iterations_without_improvement"
        },
        "robustness_features": [
            "application_to_various_TSP_instances",
            "robust_on_synthetic_and_real-world_TSPLIB data",
            "deterministic_tie-breaking"
        ],
        "interpretability": "heuristic step sequence is straightforward: construction then local search",
        "complexity": "O(n^2) for construction, O(n^3) for local search in worst case",
        "tuning_guidance": "parameters can be adjusted for instance size and complexity"
    }

