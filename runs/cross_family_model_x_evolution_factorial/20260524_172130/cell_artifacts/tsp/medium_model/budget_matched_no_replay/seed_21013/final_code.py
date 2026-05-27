def build_heuristic():
    # Deterministic heuristic scaffold for a constrained TSP-like problem.
    scaffold = {
        "name": "budget_matched_no_replay",
        "version": 1,
        "technique": "budget_matched_no_replay",
        "description": (
            "A robust, interpretable TSP-like heuristic with budget-based edge selection, "
            "no replay or memory of failures. Emphasizes transfer performance on held-out "
            "TSPLIB instances and synthetic variants."
        ),
        "parameters": {
            "budget_factor": 1.0,            # multiplier on total allowed tour length
            "initial_bias": 0.0,             # bias to start node ordering
            "edge_cost_model": "euclidean",  # distance metric: euclidean or manhattan
            "alpha": 0.5,                    # trade-off between local gain and budget adherence
            "beta": 0.0,                     # secondary penalty for constraint violations (0 means none)
            "tiebreaker": "deterministic_index",  # deterministic tiebreaker for equal options
        },
        "strategy": {
            "core_steps": [
                "select_start_node_deterministic",  # choose a fixed start index for reproducibility
                "greedy_extend_under_budget",       # extend tour by cheapest feasible edge under budget
                {"insert_middle_if_better": {
                    "condition": "improve_partial_tour",
                    "method": "swap_or_insert"
                }},
                "prune_cycles_to_maintain_connectivity",  # remove small cycles that don't contribute
            ],
            "budget_control": {
                "total_budget": {"type": "length", "value": "computed_from_instance"},
                "budget_factor": 1.0,  # runtime-configurable scale
                "allowance": "dynamic_tolerance",  # small slack to account for numeric differences
            },
            "edge_handling": {
                "neighbor_limit": 6,      # keep horizon reasonable for interpretability
                "avoid_revisit_penalty": 0.0,  # no extra penalty beyond deterministic costs
            },
        },
        "robustness": {
            "transfer_handling": {
                "held_out_tsplib": True,
                "synthetic_variants": True,
                "domain_shift": "mild",  # limit domain shift to preserve interpretability
            },
            "normalization": {
                "scale_costs": True,
                "normalize_by_max_edge": False,
            },
        },
        "output": {
            "tour_representation": "permutation_of_nodes",
            "score_report": ["total_cost", "budget_violation", "edge_count", "start_node"],
            "debug_flags": {
                "log_steps": False,
                "trace_tie_breaks": False
            }
        },
        "notes": (
            "This scaffold uses deterministic components only (no randomness, no replay/memory). "
            "It focuses on budget-aware greedy construction with simple local improvements and "
            "pruning to keep the solution interpretable and transferable."
        ),
        "constraints": {
            "no_imports": True,
            "deterministic": True
        }
    }
    return scaffold
