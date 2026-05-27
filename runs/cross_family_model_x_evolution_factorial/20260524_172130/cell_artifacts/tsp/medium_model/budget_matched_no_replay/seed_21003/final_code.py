def build_heuristic():
    # Deterministic heuristic scaffold for a constrained TSP heuristic using
    # a budget_matched_no_replay strategy. This is a lightweight, interpretable
    # template suitable for robust evaluation on held-out TSPLIB and synthetic
    # transfer sets. It does not rely on imports or replay/failure memories.

    heuristic = {
        "name": "budget_matched_no_replay_constrained_tsp",
        "description": (
            "Deterministic scaffold: construct a tour respecting a hard budget "
            "and simple constraints using a staged, interpretable approach."
        ),
        "parameters": {
            "budget_fraction": 0.9,        # fraction of total assumed budget to use for initial construction
            "min_tour_gap": 0.01,          # minimum allowed gap tolerance when refining
            "initial_step_size": 0.5,      # initial move size for constructive phase
            "refine_steps": 2,             # number of refinement passes
            "cost_function": "balanced_cost",  # placeholder name for a deterministic cost function
            "penalty_strength": 1.0,        # penalty weight for constraint violations (kept non-intrusive)
            "growth_factor": 1.0,           # no adaptive growth to maintain determinism
            "seed": 0,                      # fixed seed for any deterministic internal shuffles (no randomness)
            "max_runtime_seconds": 10,      # budget for evaluation phase (deterministic)
            "allow_revisit": False,         # keep tour construction straightforward
        },
        "construction_strategy": {
            "stages": [
                {
                    "name": "greedy_feasible_seed",
                    "description": "Build an initial feasible partial tour by greedily extending with lowest incremental cost while honoring constraints.",
                    "technique": "greedy",
                    "parameters": {
                        "seed_node": 0,
                        "step_limit": 0.25,          # fraction of vertices to visit in seed phase
                        "constraint_handling": "hard",
                    },
                },
                {
                    "name": "budget_aware_extension",
                    "description": "Extend the partial tour using budget_fraction to limit additional cost.",
                    "technique": "local_improvement",
                    "parameters": {
                        "budget_fraction": 0.9,
                        "extension_policy": "append_lowest_cost",
                        "constraint_handling": "hard",
                    },
                },
                {
                    "name": "finalization",
                    "description": "Close the tour with deterministic closing move while respecting constraints.",
                    "technique": "closure",
                    "parameters": {
                        "closure_method": "nearest_feasible",
                        "allow_unconnected": False,
                    },
                },
            ]
        },
        "constraint_model": {
            "types": ["precedence", "delivery_limit", "time_window_free"],  # abstract placeholders
            "enforcement": "hard",  # all constraints must be satisfied for a tour to be feasible
        },
        "evaluation": {
            "objective": "minimize_cost_with_constraints",
            "normalization": "per_instance",
            "heldout_policy": {
                "tsplib": True,
                "synthetic_transfer": True
            },
            "determinism": True,
        },
        "interpretability": {
            "notes": "All steps are deterministic and the strategy is transparent: seed, greedy extension, budget-limited extension, deterministic closure.",
        }
    }

    return heuristic
