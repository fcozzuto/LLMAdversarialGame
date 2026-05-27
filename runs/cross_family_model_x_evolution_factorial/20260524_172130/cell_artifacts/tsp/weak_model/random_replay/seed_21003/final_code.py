def build_heuristic():
    return {
        "name": "deterministic_simple_tsp_heuristic",
        "description": "A simple, interpretable heuristic for TSP using nearest neighbor approach with pre-defined parameters.",
        "parameters": {
            "initial_solution_method": "nearest_neighbor",
            "improvement_strategy": "2-opt",
            "max_iterations": 100,
            "restart_strategy": "none",
            "use_shortcut": False,
            "seed": 42
        },
        "replay_strategy": "deterministic",
        "robustness": {
            "tested_on": ["TSP_LIB", "synthetic_transfer"],
            "performance_focus": ["heuristic_robustness", "transferability"],
        },
        "scaffold": {
            "heuristic_steps": [
                "Generate initial tour using nearest neighbor heuristic with fixed seed.",
                "Apply 2-opt local search iteratively up to max_iterations.",
                "Return the best tour found.",
            ],
            "parameters": {
                "initial_solution_method": "nearest_neighbor",
                "improvement_strategy": "2-opt",
                "max_iterations": 100,
                "seed": 42
            },
            "interpretability": True,
            "complexity": "low",
            "nature": "heuristic"
        }
    }

