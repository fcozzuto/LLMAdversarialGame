def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for a constrained TSP heuristic with robust evaluation on held-out TSPLIB-like and synthetic transfer instances.",
        "assumptions": [
            "instances are complete graphs with non-negative edge costs",
            "constraints may include required nodes, prohibited edges, and/or sequencing requirements",
            "the heuristic must be interpretable and not overly complex",
            "deterministic behavior without randomness"
        ],
        "technique": "failure_replay_compression",
        "replay_archived_entries": [],
        "strategy": {
            "primary_objective": "minimize total tour cost while respecting node-level constraints",
            "constraint_handling": [
                "hard constraints must be satisfied in any produced tour",
                "soft constraints (if any) influence scoring but do not override hard constraints"
            ],
            "scoring_function": {
                "base_cost_weight": 1.0,
                "soft_constraint_penalty_weight": 0.0,
                "transfer_penalty_weight": 0.0,
                "robustness_tail": 0.0
            },
            "construction_method": [
                "build initial feasible tour using a deterministic greedy insertion respecting constraints",
                "apply 1-opt local improvements that preserve feasibility",
                "perform simple 2-opt or constrained swap checks to reduce cost while maintaining feasibility",
                "do not introduce randomness in tie-breaking; use deterministic orderings"
            ],
            "feasibility_checking": {
                "before_return": "verify tour visits all required nodes exactly once and adheres to constraints",
                "on_violation": "abort and return the best feasible tour found or a minimal feasible fallback"
            }
        },
        "data_handling": {
            "supported_sources": [
                "synthetic_transfer_instances",
                "held_out_TSPLIB_like_instances",
                "training-like_instances (for reference only)"
            ],
            "input_representation": {
                "nodes": "0..N-1",
                "edges": "cost matrix C where C[i][j] is the cost from i to j",
                "constraints": {
                    "required_nodes": "set of nodes that must appear in the tour",
                    "forbidden_edges": "set of (i,j) pairs that cannot be used",
                    "precedence": "optional: (a before b) constraints"
                }
            },
            "output_representation": {
                "tour": "list of node indices in visitation order starting and ending at the same node implicit",
                "cost": "total tour cost",
                "feasible": "True if constraints satisfied"
            }
        },
        "robustness_and_transfer": {
            "evaluation_focus": [
                "performance on held-out TSPLIB-like instances",
                "transferability to synthetic instances with similar structure",
                "avoid overfitting to training instances"
            ],
            "scalability": "deterministic small-to-moderate instances; linear or near-linear in N for greedy phases",
            "interpretability": "clear tie-breaking rules and deterministic steps"
        },
        "determinism": {
            "random_seed_used": False,
            "tie_breaking": "deterministic ordering by node index"
        }
    }
