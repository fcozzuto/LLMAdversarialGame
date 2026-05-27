def build_heuristic():
    return {
        "name": "deterministic_simple_heuristic",
        "techniques": ["nearest_neighbor", "2_opt"],
        "parameters": {
            "initial_solution": "nearest_neighbor",
            "local_search": "2_opt",
            "stopping_condition": "fixed_iterations",
            "max_iterations": 1000
        },
        "instance_constraints": {
            "type": ["TSPLIB", "synthetic"],
            "size": {"min": 20, "max": 1000},
            "symmetry": True,
            "triangle_inequality": True
        },
        "robustness": {
            "evaluated_on": ["eil51", "berlin52", "kroA100", "kroB100", "pr1002"],
            "performance": "heuristic to produce near-optimal solutions within reasonable time",
            "transfer": "designed for varied real-world and synthetic instances"
        },
        "interpretability": "heuristic employs well-understood algorithms with clear parameters"
    }

