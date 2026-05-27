def build_heuristic():
    return {
        "name": "constrained_tsp_heuristic_scaffold",
        "version": 1,
        "description": "Deterministic scaffold for a constrained TSP heuristic using robust, interpretable components with failure_replay_compression approach placeholder.",
        "technique": "failure_replay_compression",
        "notes": [
            "No replay archive entries available yet.",
            "Deterministic behavior ensures reproducibility across runs.",
            "Emphasizes robustness to TSPLIB-like and synthetic transfer instances.",
            "Maintains interpretability with simple, modular stages."
        ],
        "stages": [
            {
                "stage_id": "validation",
                "purpose": "Validate problem constraints and prepare problem summary.",
                "components": [
                    "check_required_fields",
                    "basic_feasibility_assessment",
                    "constraint_summary"
                ],
                "output": "problem_summary"
            },
            {
                "stage_id": "initial_solution",
                "purpose": "Generate a deterministic initial tour that respects simple constraints.",
                "components": [
                    "nearest_neighbor_step",
                    "grid_refinement",
                    "segment_shaping"
                ],
                "output": "initial_tour"
            },
            {
                "stage_id": "local_improvement",
                "purpose": "Apply conservative local optimizations to improve tour within constraint bounds.",
                "components": [
                    "2opt_like_swap",
                    "or_opt_like_adjustment",
                    "feasibility_preserving_checks"
                ],
                "output": "improved_tour"
            },
            {
                "stage_id": "failure_replay_compression",
                "purpose": "Record deterministic failure-replay signals (placeholders) to enable future replay without archives.",
                "components": [
                    "serialize_failure_signals",
                    "replay_signature_generation"
                ],
                "output": "compression_payload"
            },
            {
                "stage_id": "evaluation",
                "purpose": "Provide a transparent evaluation summary for potential transfer and robustness metrics.",
                "components": [
                    "tour_length",
                    "constraint_violation_count",
                    "robustness_hint_against_transfer"
                ],
                "output": "evaluation_report"
            }
        ],
        "parameters": {
            "constraint_tolerance": 1e-6,
            "max_iterations": 100,
            "seed": 42,
            "transfer_robustness_margin": 0.05
        },
        "expected_outputs": [
            "initial_tour",
            "improved_tour",
            "compression_payload",
            "evaluation_report"
        ],
        "compatibility": {
            "no_imports": True,
            "deterministic": True,
            "interpretable": True
        }
    }
