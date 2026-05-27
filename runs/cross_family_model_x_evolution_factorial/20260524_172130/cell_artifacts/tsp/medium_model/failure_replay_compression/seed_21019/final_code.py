def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic TSP heuristic scaffold with constraints and transfer evaluation placeholders.",
        "algorithm": {
            "type": "hybrid_constrained_greedy",
            "seed": 0,
            "steps": [
                {"step": "initialization", "details": "Create list of nodes with mandatory constraints flags if any."},
                {"step": "feasible_candidate_selection", "details": "Select next city from feasible set by a simple metric."},
                {"step": "constraint_check", "details": "Enforce all problem-specific constraints (e.g., required edges, forbidden edges)."},
                {"step": "local_improvement", "details": "Apply lightweight 2-opt or swap if improves feasibility and cost."},
                {"step": "termination", "details": "Stop when all nodes visited or no feasible extension remains."}
            ]
        },
        "constraints": {
            "mandatory_edges": [],  # list of (u, v) pairs that must be included
            "forbidden_edges": [],  # list of (u, v) pairs that must be avoided
            "must_visit_order": None,  # optional tuple (u_before_v, ...), or None
            "vehicle_capacity": None,  # optional capacity constraint
            "subtour_elimination": True
        },
        "tsp_instance_handling": {
            "scenarios": [
                {"type": "tsplib_transfer", "description": "Robustness to held-out TSPLIB instances."},
                {"type": "synthetic_transfer", "description": "Synthetic instances for transfer performance."}
            ],
            "selection_criteria": [
                "shortest_path_length",
                "constraint_violation_count",
                "computational_effort"
            ],
            "robustness_principle": "prefer solutions that generalize across held-out and synthetic instances."
        },
        "performance_metrics": {
            "inference_time_ms": 0,
            "solution_quality_bound": None,
            "transfer_score": None,
            "robustness_metric": None
        },
        "interpretability": {
            "explanation": "The heuristic uses a transparent greedy-with-constraint framework plus a small local improvement.",
            "configurable_parameters": [
                "seed",
                "feasible_candidate_limit",
                "local_improvement_depth"
            ]
        },
        "failure_replay_compression": {
            "archive_status": "No replay archive entries are available yet.",
            "fallback": "Deterministic path chosen by seed-based tie-breaking; no historical replays used."
        }
        }
