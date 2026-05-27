def build_heuristic():
    return {
        "name": "failure_replay",
        "description": "A simple, deterministic heuristic for constrained TSP based on failure replay strategy.",
        "technique": "failure_replay",
        "parameters": {
            "max_replay_attempts": 10,
            "initial_constraint_tolerance": 0.05,
            "constraint_tolerance_decay": 0.005,
            "greedy_close_threshold": 0.1,
            "allow_constraint_relaxation": True,
            "reward_for_feasible": 1.0,
            "penalty_for_infeasible": -1.0,
            "timeout_per_replay": 2.0
        },
        "heuristic_steps": [
            "Initialize with a greedy solution respecting current constraints",
            "Attempt to improve the solution by replaying failures within allowed attempts",
            "Relax constraints gradually if no feasible solution is found",
            "Record and retain best solutions for future replays",
            "Prioritize moves that reduce total tour length while satisfying constraints"
        ],
        "robustness": "Designed to balance between feasibility and optimization, demonstrated on TSPLIB and synthetic instances",
        "interpretability": "Uses straightforward greedy and relaxation techniques, easily understandable and adjustable"
    }

