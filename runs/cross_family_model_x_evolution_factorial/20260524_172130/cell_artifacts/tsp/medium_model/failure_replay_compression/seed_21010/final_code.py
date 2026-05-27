def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for constrained TSP heuristic with interpretability. Emphasizes held-out TSPLIB-like and synthetic transfer performance.",
        "technique": "failure_replay_compression",
        "replay_archive": None,
        "candidates": [
            {
                "id": "candidate_1",
                "note": "No replay archive entries available yet.",
                "strategy": "baseline-greedy-with-constraints",
                "parameters": {
                    "start_node": None,            # deterministic: choose smallest-index node
                    "build_order": "ascending",    # deterministic node visitation order
                    "constraint_check": "forward",
                    "acceptance_criterion": "feasible_and_local_improvement",
                    "lookahead": 1,                 # minimal lookahead to ensure feasibility
                    "max_steps": 1000
                },
                "behavior": {
                    "description": "Construct a feasible tour by sequentially adding the nearest feasible node respecting constraints, with strict deterministic tie-breaking.",
                    "robustness": "designed to work across synthetic and TSPLIB-like instances with simple constraint sets.",
                    "interpretability": "high; each step is a clear feasibility check and nearest-available choice."
                },
                "evaluation": {
                    "target_domains": ["held-out_TSPLIB_like", "synthetic_transfer"],
                    "metrics": ["feasibility_rate", "solution_cost", "runtime_ms"],
                    "scalability": "O(n^2) per tour in worst case; practical for moderate sizes"
                }
            }
        ],
        "constraints": {
            "no_imports": True,
            "deterministic": True,
            "maintain_interpretability": True
        },
        "notes": "Supports fail-replay compression conceptually; since no replay archive exists, this scaffold uses a simple baseline approach with deterministic behavior."
    }
