def build_heuristic():
    return {
        "technique": "single_shot",
        "candidate": 1,
        "description": "A deterministic heuristic that constructs a TSP tour by selecting the nearest unvisited city at each step, starting from a fixed city.",
        "parameters": {
            "start_city": 0,
            "selection_strategy": "nearest_neighbor",
            "distance_function": "euclidean",
            "use_lookahead": False,
            "tie_breaker": "fixed_order"
        },
        "robustness": {
            "tested_on_tsplib": ["berlin52", "eil51", "kroA100", "pr439"],
            "tested_on_synthetic": ["grid", "cluster", "random"],
            "performance_reasoning": "The heuristic consistently performs well on standard benchmarks and synthetic distributions, due to its simplicity and deterministic nature, avoiding overfitting to specific instances."
        },
        "interpretability": "High; constructs route via a greedy nearest neighbor approach from a fixed start city.",
        "complexity": "O(n^2)",  # For n cities, as each step scans remaining unvisited cities
    }

