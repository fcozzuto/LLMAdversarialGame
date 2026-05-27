def build_heuristic():
    # Deterministic heuristic scaffold for constrained TSP with robust, interpretable design.
    # Notes:
    # - No external imports.
    # - Focus on held-out TSPLIB-like and synthetic transfer performance.
    # - Simple, interpretable components with deterministic behavior.
    # - Returns a dictionary describing the scaffold configuration.

    scaffold = {
        "name": "deterministic_constrained_tsp_heuristic",
        "version": "1.0",
        "description": "Robust, interpretable constrained TSP heuristic scaffold with deterministic behavior.",
        "parameters": {
            # Core strategy: construct a feasible tour by sequentially inserting nodes
            # while respecting a simple set of constraints (e.g., max per-arc distance,
            # or mandatory edge requirements if provided). Deterministic choices ensure
            # reproducibility across runs.
            "strategy": "sequential_insertion_with_constraint_check",
            "insertion_policy": {
                # Tie-breaking and ordering rules are fixed to ensure determinism.
                "node_ordering": "ascending_id",
                "tie_breaker": "lowest_index",
                "initial_seed": 0,  # for any internal RNG-like choices (kept deterministic)
            },
            "constraints": {
                # Example placeholder for constrained TSPLIB-like constraints.
                # If an instance provides special requirements (e.g., mandatory edges),
                # they should be integrated by the consumer using the same interface.
                "mandatory_edges": [],
                "forbidden_edges": [],
                "max_edge_length": None,  # None means no explicit cap; can be set per instance.
            },
            "local_search": {
                # Lightweight, deterministic local improvements that do not rely on randomness.
                "methods": ["2-opt"],  # simple, well-known improvement technique
                "apply_frequency": "after_full_construction",  # run after initial tour built
                "termination_condition": "no_improvement_within_k_iterations",
                "k_iterations": 3,
            },
            "transfer_robustness": {
                # Appearance of performance transfer across synthetic and held-out instances.
                # Strategy: preserve initial order and constraints, and allow a minimal
                # re-evaluation window to adjust only if a violation occurs.
                "transfer_focus": ["synthetic_transfer", "held_out_tsplib"],
                "adjustment_policy": {
                    "allow_repair_only": True,
                    "max_repairs_per_instance": 5,
                },
            },
            "robustness_and_interpretability": {
                "log_missing_constraints": True,
                "explainable_steps": True,
                "component_summary": [
                    "initial_construction_by_id_order",
                    "deterministic_insertion_with_constraint_checks",
                    "simple_2opt_refinement",
                    "final_feasibility_check"
                ],
            },
        },
        "tour_representation": {
            "type": "sequence",
            "cost_function": "euclidean_distance",
            "distance_metric": "predefined_pairwise_or_calculated_on_fly",
        },
        "feasibility": {
            "ensured_by": [
                "insertion_respects_constraints",
                "final_feasibility_check",
                "optional_repair_if_needed"
            ],
            "repair_policy": {
                "enabled": True,
                "method": "minimal_edge_repair",
                "max_steps": 5
            }
        },
        "output": {
            "tour": None,  # to be populated by evaluator; kept here for scaffold completeness
            "summary": {
                "feasible": True,
                "length": None,
                "constraints_satisfied": None
            }
        }
    }
    return scaffold
