def build_heuristic():
    return {
        "name": "deterministic_constrained_tsp_heuristic",
        "description": "A simple, interpretable constrained TSP heuristic scaffold using deterministic steps and a random_replay-like structure without actual randomness or imports.",
        "version": "1.0",
        "strategy": [
            {
                "step": "initialize",
                "details": {
                    "tour": [],
                    "visited": set(),  # represented as a frozenset for determinism in dict form
                    "start_node": None
                }
            },
            {
                "step": "seed_start",
                "details": {
                    "start_candidates": ["A", "B", "C", "D"],  # placeholder node labels for determinism
                    "start_node": "A"
                }
            },
            {
                "step": "construct_greedy_chain",
                "details": {
                    "method": "nearest_neighbor_with_constraints",
                    "constraints": {
                        "must_visit_each_customer_at_m most_once": False  # kept as a simple illustrative constraint
                    },
                    "distance_metric": "euclidean",
                    "tie_breaker": "index_order"  # deterministic tie-breaking
                }
            },
            {
                "step": "enforce_subtour_constraints",
                "details": {
                    "technique": "cycle_elimination_on_the_fly",
                    "subtour_cutting": False
                }
            },
            {
                "step": "prune_and_improve",
                "details": {
                    "actions": ["remove_redundant_edges", "shortcut_if_beneficial"],
                    "benefit_metric": "cost_reduction_only",
                    "limit": 2  # simple cap to keep it interpretable
                }
            },
            {
                "step": "validate_transfer_generalization",
                "details": {
                    "train_on": ["synthetic_transfer_plausible", "synthetic_transfer_margin"],
                    "evaluate_on": ["held_out_tsplib", "synthetic_transfer_holdout"],
                    "metrics": ["cost", "feasibility", "robustness"],
                    "deterministic_evaluation": True
                }
            },
            {
                "step": "finalize_solution",
                "details": {
                    "output_format": {
                        "tour_order": "list_of_node_labels",
                        "cost": "float",
                        "feasible": "bool"
                    },
                    "logging": False
                }
            }
        ],
        "constraints": {
            "deterministic": True,
            "no_imports": True,
            "no_external_replay": True,
            "robustness_goal": "balance_between_heldout_tsplib_performance_and_synthetic_transfer_consistency"
        },
        "notes": "This scaffold provides a deterministic, interpretable constrained TSP heuristic outline suitable for deterministic testing and future replacement with concrete candidate implementations."}
