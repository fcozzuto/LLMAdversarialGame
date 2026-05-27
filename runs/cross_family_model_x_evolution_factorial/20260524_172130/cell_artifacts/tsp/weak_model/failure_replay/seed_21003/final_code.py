def build_heuristic():
    return {
        "name": "failure_replay_candidate_1",
        "technique": "failure_replay",
        "description": "A simple, robust heuristic leveraging failure replays with conservative acceptance criteria.",
        "parameters": {
            "initial_solution_strategy": "nearest_neighbor",
            "neighborhood": "2-opt",
            "max_iterations": 1000,
            "failure_threshold": 0.05,  # Accepting solutions with up to 5% worse than best so far
            "replay_limit": 50,
            "convergence_criteria": "no_improvement",
            "seed": 42
        },
        "criteria": {
            "robustness": "Prioritizes solutions that perform well on known TSPLIB instances and synthetic cases",
            "simplicity": "Uses straightforward local search with failure-based acceptance",
            "interpretability": "Parameters are explicit and easy to analyze"
        }
    }

